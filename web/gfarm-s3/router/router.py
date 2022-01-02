#from http.client import HTTPResponse
import threading
import os
#import socket
from subprocess import Popen, PIPE
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from gfarms3 import conf

logger = conf.get_logger(__name__)

def app(environ, start_response):
    (method, path, request_hdr, input, file_wrapper) = accept_request(environ)

    destURL, AccessKeyID = getDestURL(request_hdr)
    if isinstance(destURL, int):
#        logger.debug(f"@@@ {myformat()} [1] START_RESPONSE {destURL}")
        start_response(f"{destURL}", [])
        return []
    url = destURL + path

    logger.info(f"request: AccessKeyID = {AccessKeyID}, method = {method}, path = {path}")
    logger.debug(f"request_hdr = {request_hdr}")

    #logger.debug(f"@@@ METHOD {method}")
    #logger.debug(f"@@@ {method} {url} {input}")

    (response, status, response_hdr) = \
	send_request(method, url, request_hdr, input)

    #for (k, v) in response_hdr:
        #logger.debug(f"@@@ << {k}: {v}")

    if response is None:
#        logger.debug(f"@@@ {myformat()} [2] START_RESPONSE {status}")
        start_response(f"{status}", [])
        return []

    #logger.debug(f"@@@ RESPONSE {response}")
    #logger.debug(f"@@@ RESPONSE FP = {response.fp}")

    #(chunked, xAccelBuffering) = check_xAccelBuffering(response_hdr)
    xAccelBuffering = check_xAccelBuffering(response_hdr)
###    logger.debug(f"@@@ V {method} {xAccelBuffering} {path}")
#    logger.debug(f"@@@ {myformat()} [3] START_RESPONSE {status}")
    start_response(status, response_hdr)

    respiter = \
        gen_respiter(response, xAccelBuffering, file_wrapper)
        #gen_respiter(response, chunked, xAccelBuffering, file_wrapper)
#    logger.debug(f"@@@ respiter = {respiter}")
    return respiter


def accept_request(environ):
#    logger.debug(f"@@@ ACCEPT {myformat()}")
    method = environ.get("REQUEST_METHOD")
    path = environ.get("RAW_URI")
    request_hdr = [(h[5:].replace('_', '-'), environ.get(h))
                      for h in environ if h.startswith("HTTP_")]
###    logger.debug(f"@@@ ^ {method} {check_xAccelBuffering(request_hdr)} {path}")
    request_hdr = dict(request_hdr)
    #for k in request_hdr:
        #logger.debug(f"@@@ >> {k}: {request_hdr[k]}")

    content_length = environ.get("CONTENT_LENGTH")
    if content_length is not None:
        request_hdr["CONTENT-LENGTH"] = content_length
        #logger.debug(f"@@@ +++ CONTENT-LENGTH: {content_length}")

    input = environ["wsgi.input"]
    file_wrapper = environ.get("wsgi.file_wrapper", None)

    #logger.debug(f"@@@ getDestURL => {destURL}")
    #logger.debug(f"@@@ PATH => {path}")
    #logger.debug(f"@@@ URL => {url}")

    #logger.debug(f"@@@ INPUT = {type(input)}")

    return (method, path, request_hdr, input, file_wrapper)


def send_request(method, url, request_hdr, input):
#    logger.debug(f"@@@ SEND REQUEST {method} {url} [request_hdr] {input}")
    try:
        req = Request(url, input, request_hdr, method=method)
#        logger.debug(f"@@@ SEND_REQUEST {type(input)}")
        response = urlopen(req, timeout=86400)
        status = f"{response.status}"
        response_hdr = response.getheaders()
#        logger.debug(f"@@@ SUCCESS {method} {url} STATUS {status}")
    except HTTPError as e:
#        logger.debug(f"@@@ EXCEPT {e}")
        #logger.debug(f"@@@ EXCEPT code = {e.code}")
        #logger.debug(f"@@@ EXCEPT reason = {e.reason}")
        #logger.debug(f"@@@ EXCEPT headers = {e.headers}")
        #logger.debug(f"@@@ EXCEPT body = {e.read()}")
        response = e
        status = f"{e.status}"
        response_hdr = [(k, e.headers[k]) for k in e.headers]
        #logger.debug(f"@@@ EXCEPT response_hdr = {response_hdr}")
    except Exception as e:
#        logger.debug(f"@@@ EXCEPT {e}")
        #logger.debug(f"@@@ EXCEPT response = {response}")
        response = None
        status = f"{e.status}"
        response_hdr = []

    return (response, status, response_hdr)


def check_xAccelBuffering(hdr):
    #chunked = None
    xAccelBuffering = None
    for (k, v) in hdr:
        #logger.debug(f"@@@ RESPONSE HEADER k = {k}, v = {v}")
        #if k.lower() == "transfer-encoding":
            #chunked = v.lower() == "chunked"
        if k.lower() == "x-accel-buffering":
            xAccelBuffering = v.lower() != "no"

#    logger.debug(f"@@@ RESPONSE X-Accel-Buffering: {xAccelBuffering}")
    #logger.debug(f"@@@ RESPONSE Transfer-Encoding: chunked = {chunked}")
    #return (chunked, xAccelBuffering)
    return xAccelBuffering


#def gen_respiter(response, chunked, xAccelBuffering, file_wrapper):
def gen_respiter(response, xAccelBuffering, file_wrapper):
    if file_wrapper is None or xAccelBuffering == False:
#        logger.debug(f"@@@ READ1READER")
        respiter = read1Reader(response)
    else:
#        logger.debug(f"@@@ FILE_WRAPPER")
        respiter = file_wrapper(response)
    return respiter


class read1Reader():
    def __init__(self, response):
#        logger.debug(f"@@@ READ1 READER __INIT__")
        self.response = response

#    def __del__(self):
#        logger.debug(f"@@@ READ1 READER __DEL__")
#        try:
#            self.fp.close()
#        except:
#            pass

    def __iter__(self):
#        logger.debug(f"@@@ READ1 READER __ITER__")
        return self

    def __next__(self):
#        logger.debug(f"@@@ READ1 READER __NEXT__")
        amt = 8192	## same size with HTTPResponse.read()
        try:
            b = self.response.read1(amt)
            #logger.debug(f"@@@ READ1 READER b = [{debug_dumps(b)}]")
        except Exception as e:
#            logger.debug(f"@@@ READ1 READER EXCEPTION {e}")
            b = b''
        if len(b) == 0:
#            logger.debug(f"@@@ READ1 READER @@@ StopIteration")
            raise StopIteration
        return b


def getDestURL(request_hdr):
    #for key in request_hdr:
        #logger.debug(f"@@@ {key} => {request_hdr[key]}")
    AccessKeyID = getS3AccessKeyID(request_hdr.get("AUTHORIZATION"))
    if AccessKeyID is None:
        return 401
    #logger.debug(f"@@@ getDestURL: AccessKeyID = {AccessKeyID}")
    return lookupRoutingTable(AccessKeyID), AccessKeyID


def getS3AccessKeyID(Authorization):
    """
    see below for more strict implementation
    """
    if Authorization is None:
        return None
    lead = "AWS4-HMAC-SHA256 Credential="
    end = Authorization.find('/')
    if Authorization.startswith(lead) and end is not None:
        return Authorization[len(lead):end]
    return None

"""
def parse_s3_auth(authorization):
    components = authorization.split(' ')
    if "AWS4-HMAC-SHA256" not in components:
        return None
    for e in components:
        if e.startswith("Credential="):
            end = e.find('/')
            if end == -1:  
                return None
            return e[len("Credential="):end]
    return None
"""


def lookupRoutingTable(AccessKeyID):
    key = AccessKeyID	## Access Key ID itself is used for DB Key
    r = getReverseProxyRoutesDict().get(key)
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
    "lock": threading.Lock(),
    })


def getReverseProxyRoutesDict():
    global reverseProxyRoutes

    with reverseProxyRoutes["lock"]:
        path = reverseProxyRoutes["path"]
    if path is None:
        with reverseProxyRoutes["lock"]:
            path = get_gfarms3_env("GFARMS3_REVERSE_PROXY_ROUTES")
            reverseProxyRoutes["path"] = path
#            logger.debug(f"@@@ getReverseProxyRoutesDict: path = {path}")

    with reverseProxyRoutes["lock"]:
        _dict = reverseProxyRoutes["dict"]
        timestamp = reverseProxyRoutes["timestamp"]

    timestamp_file = os.stat(path).st_mtime
    if _dict is None or timestamp < timestamp_file:
#        logger.debug(f"@@@ getReverseProxyRoutesDict: loadReverseProxyRoutesDict()")
        _dict = loadReverseProxyRoutesDict(path)
        with reverseProxyRoutes["lock"]:
            if reverseProxyRoutes["timestamp"] >= timestamp_file:
                # lose the race
#                logger.debug(f"@@@ getReverseProxyRoutesDict: lose")
                _dict = reverseProxyRoutes["timestamp"]
            else:
#                logger.debug(f"@@@ getReverseProxyRoutesDict: update")
                reverseProxyRoutes["dict"] = _dict
                reverseProxyRoutes["timestamp"] = timestamp_file

#    logger.debug(f"@@@ getReverseProxyRoutesDict: _dict = {_dict}")
    return _dict


def loadReverseProxyRoutesDict(path):
    ## NOTE: Expensive operation
    with open(path, "r") as f:
        return dict([(e[0], [e[1].strip()]) for e in
                         [e.split('\t') for e in f.readlines()]])


def get_gfarms3_env(key):
    return conf.get_str(key)


def myformat(t=None):
    if t is None:
        t = time.time()
    i = time.strftime("%Y%m%dT%H%M%S", time.gmtime(t))
    f = (int)((t % 1) * 1000000)
    return "{}.{:06d}Z".format(i, f)


#def debug_dumps(s):
#    r = ""
#    for c in s:
#        if ord(' ') <= c and c <= ord('~'):
#            r += f"{chr(c)}"
#        elif c == ord('\t'):
#            r += "\\t"
#        elif c == ord('\n'):
#            r += "\\n"
#        elif c == ord('\r'):
#            r += "\\r"
#        elif c == ord('\\'):
#            r += "\\\\"
#        else:
#            r += "\\{0:03o}".format(c)
#    return r
