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

def index(request):
    return render(request, "console/index.html", {})

def application(request):
#    if request.session["result"] is no None:
#        request.session["result"].["status"] == "success" ....
#      redirect(request, "console/session-menu.html", {})
### session-menu.html page has "logout" button (that delets `session')
### , "getfacl" button
   
    return render(request, "console/application.html", {})

def launch(request):
    logger.debug("{}\n".format(request.POST))
    username = request.POST["username"]
    passwd = request.POST["passwd"]
    action = request.POST["action"]
    logger.debug("username = {}\npasswd = {}\naction = {}\n".format(username, passwd, action))
    result = cmd.cmd(username, passwd, action)
    logger.debug("result = {}\n".format(result))
    request.session["result"] = result 
    return HttpResponseRedirect(reverse("result"))

def result(request):
    #status = get_object_or_404(Status, pk = status_id)
    result = request.session["result"]
    return render(request, "console/result.html", result)
