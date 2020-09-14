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
        cmd_result = cmd.cmd(username, passwd, "start")
        if cmd_result is None or cmd_result["status"] != "success":
            request.session["status"] = "error"
            return HttpResponseRedirect(reverse("login"))
        logger.debug("cmd_result = {}".format(cmd_result))
        request.session["cmd_result"] = cmd_result 
        request.session["status"] = "success" 
        request.session["username"] = username
        return HttpResponseRedirect(reverse("result"))

def result(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    cmd_result = request.session["cmd_result"]
    return render(request, "console/result.html", cmd_result)

def list(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    username = "user1"
    bucketlist = cmd.get_bucket_list(username)
    return render(request, "console/list.html", {"bucketlist": bucketlist})

def aclfile(request):
    if need_login(request.session):
        return HttpResponseRedirect(reverse("login"))
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        logger.debug("request.POST = {}".format(request.POST))
        for key, value in request.POST.items():
            logger.debug("{} = {}".format(key, value))



    username = "user1"
    bucket_acl = cmd.get_bucket_acl(username, "mybucket")
    metainfo = [e for e in bucket_acl if e.startswith("#")]
    bucket_acl = [e for e in bucket_acl if not e.startswith("#") and e != ""]
    (groups, users) = cmd.get_users_groups_list(username)
    #logger.debug("groups = {}".format(groups))
    #logger.debug("users = {}".format(users))
    return render(request, "console/aclfile.html", {"bucket_acl": bucket_acl, "metainfo": metainfo, "groups_users": groups + users})
