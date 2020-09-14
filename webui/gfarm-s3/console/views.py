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
    logger.debug("@@@ session = {}\n".format(request.session))
    for key, value in request.session.items():
        logger.debug("@@@ {} => {}".format(key, value))
    return render(request, "console/index.html", {})

def login(request):
    if request.method == 'GET':
        isLoginFailed = is_login_failed(request.session)
        return render(request, "console/login.html", {"isLoginFailed": isLoginFailed})
    elif request.method == 'POST':

        logger.debug("request.method = {}".format(request.method))
 
        logger.debug("request.POST = {}".format(request.POST))
 
        username = request.POST["username"]
        passwd = request.POST["passwd"]
        logger.debug("username = {} --- passwd = {}".format(username, passwd))
        cmd_result = cmd.cmd("start", username, passwd)
        if cmd_result is None or cmd_result["status"] != "success":
            request.session["global_username"] = ""
            return HttpResponseRedirect(reverse("login"))
        logger.debug("cmd_result = {}".format(cmd_result))
        request.session["global_username"] = username
        request.session["authenticated_method"] = cmd_result["authenticated_method"]
        return HttpResponseRedirect(reverse("result"))

def result(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    cmd_result = cmd.cmd("info", username, "", authenticated = authenticated)
    #cmd_result = request.session["cmd_result"]
    #cmd_result = {}
    logger.debug("cmd_result = {}".format(cmd_result))
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

def edict(e):
    r = e.split(":")
    return {"id": r[0] + ":" + r[1], "perm": r[2]}

def aclfile(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))

    username = request.session["global_username"]

    if request.method == 'GET':
        logger.debug("request.GET = {}".format(request.GET))
        for key, value in request.GET.items():
            logger.debug("{} = {}".format(key, value))
        bucket = request.GET["bucket"]
    elif request.method == 'POST':
#        logger.debug("request.POST = {}".format(request.POST))
#        for key, value in request.POST.items():
#            logger.debug("{} = {}".format(key, value))
#
        bucket = request.POST["bucket"]
        cmd.set_bucket_acl(username, bucket, request.POST)

    original_bucket_acl = cmd.get_bucket_acl(username, bucket)
    bucket_acl_split = [e for e in original_bucket_acl.split('\n') if e != ""]
    acl_0 = [e for e in bucket_acl_split if is_metainfo(e)]
    acl_1 = [e for e in bucket_acl_split if is_unmodifiable(e)]
    acl_2 = [e for e in bucket_acl_split if is_modifiable(e)]
    acl_2_split = [edict(e) for e in acl_2]
    (groups, users) = cmd.get_groups_users_list(username)
    #logger.debug("groups = {}".format(groups))
    #logger.debug("users = {}".format(users))
    logger.debug("acl_0 = {}".format(acl_0))
    logger.debug("acl_1 = {}".format(acl_1))
    logger.debug("acl_2 = {}".format(acl_2))
    dict = {"bucket": bucket,
            "acl_0": acl_0,
            "acl_1": acl_1,
            "acl_2": acl_2,
            "acl_2_split": acl_2_split,
            "groups_users": groups + users,
            "acl_1_string": "\n".join(acl_1)}
    return render(request, "console/aclfile.html", dict)
