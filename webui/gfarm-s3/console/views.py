from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import logging
from . import cmd

### XXX debug
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

### session["status"]:   "success"   login succeeded
###                      "error"     login failed
###                      no-key      login never tried

def is_login_failed(session):
    if session is None or not "status" in session:
        return False
    return session["status"] != "success"

def need_login(session):
    if session is None or not "status" in session:
        return True
    return session["status"] != "success"

def index(request):
### XXX debug
    sys.stderr.write("@@@ session = {}\n".format(request.session))
    for key, value in request.session.items():
        sys.stderr.write("@@@ {} => {}".format(key, value))
    return render(request, "console/index.html", {})

def application(request):
#    if request.session["result"] is no None:
#        request.session["result"].["status"] == "success" ....
#      redirect(request, "console/session-menu.html", {})
### session-menu.html page has "logout" button (that delets `session')
### , "getfacl" button

    isLoginFailed = is_login_failed(request.session)
    return render(request, "console/application.html", {"isLoginFailed": isLoginFailed})

def launch(request):
    logger.debug("{}\n".format(request.POST))

### XXX debug
    sys.stderr.write("POST = {}\n".format(request.POST))
    sys.stderr.write("@@@ session = {}\n".format(request.session))

    username = request.POST["username"]
    passwd = request.POST["passwd"]
    #action = request.POST["action"]
    logger.debug("username = {}\npasswd = {}\n".format(username, passwd))
    cmd_result = cmd.cmd(username, passwd, "start")
    if cmd_result is None or cmd_result["status"] != "success":
        request.session["status"] = "error"
        return HttpResponseRedirect(reverse("application"))
    logger.debug("cmd_result = {}\n".format(cmd_result))
    request.session["cmd_result"] = cmd_result 
    request.session["status"] = "success" 
    request.session["username"] = username
    return HttpResponseRedirect(reverse("result"))

def result(request):
    #status = get_object_or_404(Status, pk = status_id)
    if need_login(request.session):
        return HttpResponseRedirect(reverse("application"))
    cmd_result = request.session["cmd_result"]
    return render(request, "console/result.html", cmd_result)

def list(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("application"))
    username = "user1"
    bucketlist = cmd.get_bucket_list(username)
    return render(request, "console/list.html", {"bucketlist": bucketlist})

def aclfile(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("application"))
    username = "user1"
    bucket_acl = cmd.get_bucket_acl(username, "mybucket")
    metainfo = [e for e in bucket_acl if e.startswith("#")]
    bucket_acl = [e for e in bucket_acl if not e.startswith("#") and e != ""]

    users = cmd.get_user_list(username)
    users = [e for e in users if e != ""]
    users = users[:4]

    groups = cmd.get_group_list(username)
    groups = [e for e in groups if e != ""]
    groups = groups[:4]

### XXX debug
    sys.stderr.write("USERS = {}\n".format(users))
    sys.stderr.write("GROUPS = {}\n".format(groups))

    return render(request, "console/aclfile.html", {"bucket_acl": bucket_acl, "metainfo": metainfo, "users": users, "groups": groups})
