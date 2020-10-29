from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import time
import logging
from . import cmd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

def login(request):
    if request.method == "GET":
        isLoginFailed = is_login_failed(request.session)
        isReauth = not need_login(request.session)
        username = None
        if request.session is not None:
            username = request.session.get("global_username", None)
        render_dict = {"isLoginFailed": isLoginFailed,
                       "showLogoutButton": isReauth,
                       "showReauthMsg": isReauth,
                       "username": username}
        return render(request, "console/login.html", render_dict)
    elif request.method == "POST":
        username = request.POST["username"]
        passwd = request.POST["passwd"]
        http_x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", None)
        if http_x_forwarded_for is not None:
            remote_addr = http_x_forwarded_for 
        else:
            remote_addr = request.META.get("REMOTE_ADDR", None)
        ### challenge authenticateion
        cmd_result = cmd.cmd("info", username, passwd, remote_addr = remote_addr)
        if cmd_result is None or cmd_result["status"] != "success":
            request.session["global_username"] = ""
            return HttpResponseRedirect(reverse("login"))
        request.session["global_username"] = username
        request.session["authenticated_method"] = cmd_result["authenticated_method"]
        return HttpResponseRedirect(reverse("result"))

def logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse("login"))

def reauth(request):
    return HttpResponseRedirect(reverse("login"))

def starts3(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    ### start MinIO, without authenticateion
    cmd.cmd("start", username, "", authenticated = authenticated)
    ### ignore cmd.cmd return status
    return HttpResponseRedirect(reverse("result"))

def stops3(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    cmd.cmd("stop", username, "", authenticated = authenticated)
    ### ignore cmd.cmd return status
    return HttpResponseRedirect(reverse("result"))

def chgkey(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    cmd_result = cmd.cmd("keygen", username, "", authenticated = authenticated)
    render_dict = cmd_result
    # not used: render_dict["s3sstatus"] = s3sstatus
    render_dict["showLogoutButton"] = True
    render_dict["username"] = username
    return render(request, "console/chgkeyresult.html", render_dict)

def result(request):
    lang = request.LANGUAGE_CODE
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    authenticated = request.session["authenticated_method"]
    cmd_result = cmd.cmd("info", username, "", authenticated = authenticated, lang = lang)
    s3sstatus = "s3server_status" in cmd_result and cmd_result["s3server_status"].startswith("200")
    render_dict = cmd_result
    render_dict["s3sstatus"] = s3sstatus
    render_dict["showLogoutButton"] = True
    render_dict["username"] = username
    return render(request, "console/result.html", render_dict)

def list(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    bucketlist = cmd.get_bucket_list(username)
    render_dict = {"bucketlist": bucketlist,
                   "showLogoutButton": True,
                   "username": username}
    return render(request, "console/list.html", render_dict)

def is_modifiable(s):
    return not (s.startswith("#") or "::" in s or s.startswith("default:") or s.startswith("mask:"))

def split_lines(s):
    return [e.strip() for e in s.split('\n') if e.strip() != ""]

def opt_to_perm(o):
    #logger.debug("opt_to_perm: o = \"{}\"".format(o))
    if o is None:
        #logger.debug("opt_to_perm: NONE".format(o))
        return "---"
    if o == "r":
        #logger.debug("opt_to_perm: RO".format(o))
        return "r-x"
    if o == "w":
        #logger.debug("opt_to_perm: RW".format(o))
        return "rwx"
    #logger.debug("opt_to_perm: FALLBACK: NONE".format(o))
    return "---"

def etoent(e, p):
    #logger.debug("etoent: e = {}".format(e))
    #logger.debug("etoent: p[e] = {}".format(p[e]))
    if p[e] == "0":
        return None
    opt = p.get(e.replace("sel", "opt"), None)
    #logger.debug("etoent: opt = {}".format(opt))
    perm = opt_to_perm(opt) 
    return p[e] + ":" + perm

def aclfile(request):
    lang = request.LANGUAGE_CODE
    cmd_status = False
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = request.session["global_username"]
    if request.method == "GET":
        bucket = request.GET["bucket"]
    elif request.method == "POST":
        p = request.POST
        #logger.debug("p: [{}]".format(p))
        bucket = p["bucket"]
        acl_original = split_lines(p["acl_original_string"])

        q = [e for e in p if e.startswith("sel:")]
        #logger.debug("q: [{}]".format(q))
        acl_edited = [etoent(e, p) for e in q]
        acl_edited = [e for e in acl_edited if e is not None]
        #logger.debug("acl_edited: [{}]".format(acl_edited))

        cmd.set_bucket_acl(username, bucket, acl_original, acl_edited)
        cmd_status = True
    bucket_acl = cmd.get_bucket_acl(username, bucket)
    acl_modifiable = [e for e in bucket_acl if is_modifiable(e)]
    (groups, users) = cmd.get_groups_users_list(username)
    acl_modifiable_entries = [{"entry": make_entry(e, groups + users, i + 2)} for i, e in enumerate(acl_modifiable)]
    group_perm = get_group_perm(bucket_acl)
    acl_modifiable_entries.insert(0, {"entry": make_fixed_entry("gfarms3webui:GROUP", "MY GROUP", 0, group_perm)})
    other_perm = get_other_perm(bucket_acl)
    acl_modifiable_entries.insert(1, {"entry": make_fixed_entry("gfarms3webui:OTHER", "OTHER", 1, other_perm)})
    o = [e for e in bucket_acl if e.startswith("# owner")]
    g = [e for e in bucket_acl if e.startswith("# group")]
    bucket_owner = o[0].split('# owner: ')[1]
    bucket_group = g[0].split('# group: ')[1]
    render_dict = {"bucket": bucket,
                   "acl_modifiable_entries": acl_modifiable_entries,
                   "seq": len(acl_modifiable_entries) + 2,
                   "groups_users": groups + users,
                   "acl_original_string": "\n".join(bucket_acl),
                   "showLogoutButton": True,
                   "cmd_status": cmd_status,
                   "date": cmd.myctime(time.time(), lang),
                   "username": username,
                   "bucket_owner": bucket_owner,
                   "bucket_group": bucket_group}
    return render(request, "console/aclfile.html", render_dict)

def get_group_perm(bucket_acl):
    grp = [e for e in bucket_acl if e.startswith("group::")][0]
    return get_perm(grp)

def get_other_perm(bucket_acl):
    oth = [e for e in bucket_acl if e.startswith("other::")][0]
    return get_perm(oth)

def get_perm(s):
    perm = s.split(':')[2]
    #logger.debug("perm: {}".format(perm))
    if  perm.startswith("rwx"):
        return "rwx"
    elif perm.startswith("r-x"):
        return "r-x"
    else:
        return "---"

def make_fixed_entry(id, text, seq, perm):
    seq = str(seq)
    return new_entry("li_" + seq, id, text, "sel:" + seq, "opt:" + seq, perm, False, seq)

def make_entry(e, gu, seq):
    r = e.split(':')
    id = r[0] + ":" + r[1]
    perm = r[2]
    text = [x for x in gu if x["id"] == id][0]["text"]
    seq = str(seq)
    return new_entry("li_" + seq, id, text, "sel:" + seq, "opt:" + seq, perm, True, seq)

def new_entry(id, e_id, e_text, select_name, opt_name, checked_perm, is_del_button, seq):
    #logger.debug(\"checked_perm = {}\".format(checked_perm))
    return ("<tr id=\"" + id + "\">" +
	"<td>" +
        del_button(id, is_del_button) +
	"</td>" +
	"<td>" +
        "<input type=\"hidden\" name=\"" + select_name + "\" value=\"" + e_id + "\" />" +
        "<div class=\"col-10 text-break\">" + e_text + "</div>" +
	"</td>" +
	"<td class=\"width: 40px align-middle pl-2 pr-2\">" +
        slider_round(f_button("r", opt_name, "RO", checked_perm.startswith("r"), seq)) +
	"</td>" +
	"<td class=\"width: 40px align-middle pl-2 pr-2\">" +
        slider_round(f_button("w", opt_name, "RW", checked_perm.startswith("rw"), seq)) +
	"</td>" +
        "</tr>")

def slider_round(s):
    return ("<div><label class=\"switch\">" +
        s +
        "<span class=\"slider round\"></span></label></div>")

def f_button(typ, name, text, checked, seq):
    c = ""
    if checked:
        c = " checked"
    if typ == "r":
        id = "cr_" + seq
        xid = "cw_" + seq
        xset = "false"
        cond = "!"
    else:
        id = "cw_" + seq
        xid = "cr_" + seq
        xset = "true"
        cond = ""
    #modified = "window.onbeforeunload = function() { return '!'; };"
    clear_msg = "$('#msg').empty();"
    activate_apl = "$('#apl').prop('disabled', false);"
    onclick = "if (" + cond + "$('#" + id + "').prop('checked')) { $('#" + xid + "').prop('checked', " + xset + "); }"
    return "<input type=\"checkbox\" class=\"default\" name=\"" + name + "\" id=\"" + id + "\" value=\"" + typ + "\" data-toggle=\"toggle\" onClick=\"" + clear_msg + activate_apl + onclick + "\"" + c + "/>"

def del_button(id, f):
    x = "<svg width=\"2em\" height=\"2em\" viewBox=\"0 0 16 16\" class=\"bi bi-x\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z\"/></svg>"
    clear_msg = "$('#msg').empty();"
    activate_apl = "$('#apl').prop('disabled', false);"
    onclick = "$('#" + id + "').remove();"
    if f:
        cla = "text-danger"
    else:
        cla = "text-secondary disabled"
    return "<button type=\"button\" class=\"btn btn-link btn-sm " + cla + "\" onClick=\"" + clear_msg + activate_apl + onclick + "\">" + x + "</button>"
