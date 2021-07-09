from http.client import HTTPResponse
from logging import getLogger, DEBUG, INFO, WARNING
from logging.handlers import SysLogHandler
import threading
import os
import socket
from subprocess import Popen, PIPE
import time
from myurllib import myUrllib

handler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL7)
logger = getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(DEBUG)

gfarm_s3_conf = "/usr/local/etc/gfarm-s3.conf"


def myformat(t=None):
    if t is None:
        t = time.time()
    i = time.strftime("%Y%m%dT%H%M%S", time.gmtime(t))
    f = (int)((t % 1) * 1000000)
    return "{}.{:06d}Z".format(i, f)


def app(environ, start_response):
    (method, path, request_hdr, input, file_wrapper) = accept_request(environ)

    myurllib = myUrllib()

    destURL = getDestURL(request_hdr)
    if isinstance(destURL, int):
#        logger.debug(f"@@@ -- START_RESPONSE {destURL}")
        start_response(f"{destURL}", [])
        return []
    url = destURL + path

#    logger.debug(f"@@@ METHOD {method}")
    #logger.debug(f"@@@ {method} {url} {input}")

    (response, status, response_hdr) = \
	myurllib.send_request(method, url, request_hdr, input)

    if response is None:
        logger.debug(f"@@@ {myformat()} START_RESPONSE {status}")
        start_response(f"{status}", [])
        return []

#    logger.debug(f"@@@ RESPONSE {response}")
#    logger.debug(f"@@@ RESPONSE FP = {response.fp}")

    (chunked, xAccelBuffering) = parse_response_hdr(response_hdr)
    logger.debug(f"@@@ {myformat()} START_RESPONSE {status}")
    write = start_response(status, response_hdr)

    respiter = \
        myurllib.gen_respiter(response, write, chunked, xAccelBuffering, file_wrapper)
    logger.debug(f"@@@ respiter = {respiter}")
    return respiter

        #write = start_response(status, xxxheaders)
            # (void)write
        #return rawRelay(write, response)


def accept_request(environ):
    logger.debug(f"@@@ ACCEPT {myformat()}")
    method = environ.get("REQUEST_METHOD")
    path = environ.get("RAW_URI")
    request_hdr = [(h[5:].replace('_', '-'), environ.get(h))
                      for h in environ if h.startswith("HTTP_")]
    request_hdr = dict(request_hdr)
#    for k in request_hdr:
#        logger.debug(f"@@@ >> {k}: {request_hdr[k]}")

    content_length = environ.get("CONTENT_LENGTH")
    if content_length is not None:
        request_hdr["CONTENT-LENGTH"] = content_length
#        logger.debug(f"@@@ +++ CONTENT-LENGTH: {content_length}")

    input = environ.get("wsgi.input")
    file_wrapper = environ["wsgi.file_wrapper"]

#    logger.debug(f"@@@ getDestURL => {destURL}")
#    logger.debug(f"@@@ PATH => {path}")
#    logger.debug(f"@@@ URL => {url}")

#    logger.debug(f"@@@ INPUT = {type(input)}")

    return (method, path, request_hdr, input, file_wrapper)


def parse_response_hdr(response_hdr):
    chunked = None
    xAccelBuffering = None
    for (k, v) in response_hdr:
#        logger.debug(f"@@@ RESPONSE HEADER k = {k}, v = {v}")
        if k.lower() == "transfer-encoding":
            chunked = v.lower() == "chunked"
        if k.lower() == "x-accel-buffering":
            xAccelBuffering = v.lower() != "no"

    logger.debug(f"@@@ RESPONSE X-Accel-Buffering: {xAccelBuffering}")
    logger.debug(f"@@@ RESPONSE Transfer-Encoding: chunked = {chunked}")
    return (chunked, xAccelBuffering)


def getDestURL(request_hdr):
    #for key in request_hdr:
    #    logger.debug(f"@@@ {key} => {request_hdr[key]}")
    AccessKeyID = getS3AccessKeyID(request_hdr.get("AUTHORIZATION"))
    if AccessKeyID is None:
        return 401
    #logger.debug(f"@@@ getDestURL: AccessKeyID = {AccessKeyID}")
    return lookupRoutingTable(AccessKeyID)


def getS3AccessKeyID(Authorization):
    if Authorization is None:
        return None
    lead = "AWS4-HMAC-SHA256 Credential="
    end = Authorization.find('/')
    if Authorization.startswith(lead) and end is not None:
        return Authorization[len(lead):end]
    return None


def lookupRoutingTable(AccessKeyID):
    key = AccessKeyID	## Access Key ID itself is used for DB Key
    r = getReverseProxyRoutesDict(gfarm_s3_conf).get(key)
    #logger.debug(f"@@@ lookupRoutingTable: {AccessKeyID} => {r}")
    if r is None:
        return 503
    destURL = r[0]	## extract URL part
    #logger.debug(f"@@@ lookupRoutingTable: destURL = {destURL}")
    if destURL is None:
        return 503
    #logger.debug(f"@@@ {AccessKeyID} => {destURL}")
    return destURL


reverseProxyRoutes = dict({
    "dict": None,
    "path": None,
    "timestamp": 0,
    "lastchecked": 0,
    "statInterval": 1,
    "lock": threading.Lock(),
    })


def getReverseProxyRoutesDict(gfarm_s3_conf):
    global reverseProxyRoutes
    path = reverseProxyRoutes["path"] 
    if path is None:
        with reverseProxyRoutes["lock"]:
            path = get_gfarms3_env(gfarm_s3_conf, "GFARMS3_REVERSE_PROXY_ROUTES")
            reverseProxyRoutes["path"] = path 
            #logger.debug(f"@@@ getReverseProxyRoutesDict: path = {path}")
    dict = reverseProxyRoutes["dict"]
    timestamp = reverseProxyRoutes["timestamp"]
    timestamp_file = timestamp
    now = time.time()
    if (reverseProxyRoutes["lastchecked"] + 
        reverseProxyRoutes["statInterval"]) < now:
        #logger.debug(f"@@@ getReverseProxyRoutesDict: STAT elapsed = {now - reverseProxyRoutes["lastchecked"]}")
        with reverseProxyRoutes["lock"]:
            reverseProxyRoutes["lastchecked"] = now
        timestamp_file = os.stat(path).st_mtime
    if dict is None or timestamp < timestamp_file:
        dict = loadReverseProxyRoutesDict(path)
        logger.debug(f"@@@ WITH LOCK")
        with reverseProxyRoutes["lock"]:
            ## although timestamp_file is calculated before obtaining current
            ## lock, this operation is still safe.  probably....
            reverseProxyRoutes["dict"] = dict
            reverseProxyRoutes["timestamp"] = timestamp_file  
    #logger.debug(f"@@@ getReverseProxyRoutesDict: dict = {dict}")
    return dict


def loadReverseProxyRoutesDict(path):
    ## WARNING: Expensive operation
    with open(path, "r") as f:
        return dict([(e[0], [e[1].strip()]) for e in
                         [e.split('\t') for e in f.readlines()]])


def get_gfarms3_env(gfarm_s3_conf , key):
    ## WARNING: Expensive operation
    cmd = ["sh", "-c", f". {gfarm_s3_conf}; printf \"%s\" ${key}"]
    with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as p:
        (out, err) = p.communicate()
        p.wait()
    return out.decode()
