from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import logging
from . import cmd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

### session["global_username"]:
###   "non-empty"  login succeeded
###   ""           login failed
###   no-key       login never tried

def is_login_failed(session):
    if session is None or not "global_username" in session:
        return False
    return session["global_username"] == ""

def need_login(session):
    if session is None or not "global_username" in session:
        return True
    return session["global_username"] == ""

def index(request):
    return render(request, "console/index.html", {})

def login(request):
    if request.method == 'GET':
        isLoginFailed = is_login_failed(request.session)
        return render(request, "console/login.html", {"isLoginFailed": isLoginFailed})
    elif request.method == 'POST':
        username = request.POST["username"]
        passwd = request.POST["passwd"]
        ### challenge authenticateion and start MinIO
        cmd_result = cmd.cmd("start", username, passwd)
        if cmd_result is None or cmd_result["status"] != "success":
            request.session["global_username"] = ""
            return HttpResponseRedirect(reverse("login"))
        request.session["global_username"] = username
        request.session["authenticated_method"] = cmd_result["authenticated_method"]
        return HttpResponseRedirect(reverse("result"))

def logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse("login"))
    return render(request, "console/login.html", {})

def starts3(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    ### start MinIO, without authenticateion
    cmd.cmd("start", username, "", authenticated = authenticated)
    ### ignore cmd.cmd return value
    return HttpResponseRedirect(reverse("result"))

def stops3(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    cmd.cmd("stop", username, "", authenticated = authenticated)
    ### ignore cmd.cmd return value
    return HttpResponseRedirect(reverse("result"))

def chgkey(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    if request.method == 'POST':
        running = request.POST["s3sstatus"]
    else:
        running = False
    logger.debug("RUNNING = {}".format(running))
    if running:
        cmd.cmd("stop", username, "", authenticated = authenticated)
    cmd.cmd("keygen", username, "", authenticated = authenticated)
    if running:
        cmd.cmd("start", username, "", authenticated = authenticated)
    ### ignore cmd.cmd return value
    return HttpResponseRedirect(reverse("result"))

def result(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    cmd_result = cmd.cmd("info", username, "", authenticated = authenticated)
    cmd_result["s3sstatus"] = "s3server_status" in cmd_result and cmd_result["s3server_status"].startswith("200")
    return render(request, "console/result.html", cmd_result)

def list(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    bucketlist = cmd.get_bucket_list(username)
    return render(request, "console/list.html", {"bucketlist": bucketlist})

def is_metainfo(s):
    return s.startswith("#")

def is_unmodifiable(s):
    return not is_metainfo(s) and ("::" in s or s.startswith("default:"))

def is_modifiable(s):
    return not is_metainfo(s) and "::" not in s and not s.startswith("default:")

def is_active(perm, expect):
    if perm == expect:
        return " active"
    return ""

def is_checked(perm, expect):
    if perm == expect:
        return " checked"
    return ""

def edict(e, gu):
    r = e.split(":")
    id = r[0] + ":" + r[1]
    perm = r[2]
    text = [x for x in gu if x["id"] == id][0]["text"]
    a0 = is_active(perm, "rwx")
    a1 = is_active(perm, "r-x")
    a2 = is_active(perm, "---")
    c0 = is_checked(perm, "rwx")
    c1 = is_checked(perm, "r-x")
    c2 = is_checked(perm, "---")
    return {"id": id, "text": text,
            "a0": a0, "a1": a1, "a2": a2,
            "c0": c0, "c1": c1, "c2": c2}

def aclfile(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    if request.method == 'GET':
        bucket = request.GET["bucket"]
    elif request.method == 'POST':
        p = request.POST
        bucket = p["bucket"]
        acl_1_string = p["acl_1_string"]
        q = [e for e in p if e.startswith("opt:")]
        acl_2 = [p[e.replace("opt", "sel")] + ":" + p[e] for e in q]
        cmd.set_bucket_acl(username, bucket, acl_1_string, acl_2)
    bucket_acl = cmd.get_bucket_acl(username, bucket)
    acl_0 = [e for e in bucket_acl if is_metainfo(e)]
    acl_1 = [e for e in bucket_acl if is_unmodifiable(e)]
    acl_2 = [e for e in bucket_acl if is_modifiable(e)]
    (groups, users) = cmd.get_groups_users_list(username)
    dict = {"bucket": bucket,
            "acl_0": acl_0,
            "acl_1": acl_1,
            "acl_2": acl_2,
            "acl_2_preset": [edict(e, groups + users) for e in acl_2],
            "groups_users": groups + users,
            "acl_1_string": "\n".join(acl_1),
            "seq": len(acl_2)}
    return render(request, "console/aclfile.html", dict)
