import os
import sys
from subprocess import Popen, PIPE
import urllib.request
import time

gfarm_s3_conf = "/usr/local/etc/gfarm-s3.conf"


def myformat(t):
    i = time.strftime('%Y%m%dT%H%M%S', time.gmtime(t))
    f = (int)((t % 1) * 1000000)
    return "{}.{:06d}Z".format(i, f)


def app(environ, start_response):
    now = time.time()
    #sys.stderr.write(f"@@@ ACCEPT {myformat(now)}\n")
    headers = [(h[5:].replace('_', '-'), environ.get(h))
                  for h in environ if h.startswith("HTTP_")]
    headers = dict(headers)
    #for k in headers:
        #sys.stderr.write(f"@@@ >>> {k}: {headers[k]}\n")
    content_length = environ.get("CONTENT_LENGTH")
    if content_length is not None:
        headers["CONTENT-LENGTH"] = content_length

    destURL = getDestURL(headers)
    if isinstance(destURL, int):
        sys.stderr.write(f"@@@ app: {destURL}\n")
        start_response(f"{destURL}", [])
        return []

    path = environ.get("RAW_URI")
    url = destURL + path

    #sys.stderr.write(f"@@@ getDestURL => {destURL}\n")
    #sys.stderr.write(f"@@@ path = {path}\n")
    #sys.stderr.write(f"@@@ url = {url}\n")

    input = environ.get("wsgi.input")

    method = environ.get("REQUEST_METHOD")

    sys.stderr.write(f"{myformat(now)} {method} {path}\n")

    req = urllib.request.Request(url, input, headers, method=method)

    try:
        res = urllib.request.urlopen(req, timeout=86400)
        status = f"{res.status}"
        headers = res.getheaders()
        sys.stderr.write(f"{myformat(now)} SUCCESS status = {status}\n")

    except Exception as e:
        res = None
        status = f"{e.status}"
        headers = [(k, e.headers[k]) for k in e.headers]
        sys.stderr.write(f"{myformat(now)} EXCEPT status = {status}\n")

    #sys.stderr.write(f"@@@ res: {type(res)}\n")

    start_response(status, headers)
    now = time.time()
    #sys.stderr.write(f"@@@ RESPONSE {myformat(now)}\n")
    if res is None:
        return []
    return environ['wsgi.file_wrapper'](res)


def getDestURL(headers):
    #for key in headers:
    #    sys.stderr.write(f"@@@ {key} => {headers[key]}\n")
    AccessKeyID = getS3AccessKeyID(headers.get("AUTHORIZATION"))
    if AccessKeyID is None:
        return 401
    #sys.stderr.write(f"@@@ getDestURL: AccessKeyID = {AccessKeyID}\n")
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
    #sys.stderr.write(f"@@@ lookupRoutingTable: {AccessKeyID} => {r}\n")
    if r is None:
        return 503
    url = r[0]	## extract URL part
    #sys.stderr.write(f"@@@ lookupRoutingTable: url = {url}\n")
    if url is None:
        return 503
    #sys.stderr.write(f"@@@ {AccessKeyID} => {url}\n")
    return url


reverseProxyRoutes = dict({
    "dict": None,
    "path": None,
    "timestamp": 0,
    "lastchecked": 0,
    })

def getReverseProxyRoutesDict(gfarm_s3_conf):
    global reverseProxyRoutes
    statInterval = 1
    path = reverseProxyRoutes["path"] 
    if path is None:
        path = get_gfarms3_env(gfarm_s3_conf, "GFARMS3_REVERSE_PROXY_ROUTES")
        reverseProxyRoutes["path"] = path 
        #sys.stderr.write(f"@@@ getReverseProxyRoutesDict: path = {path}\n")
    dict = reverseProxyRoutes["dict"]
    timestamp = reverseProxyRoutes["timestamp"]
    timestamp_file = timestamp
    now = time.time()
    if reverseProxyRoutes["lastchecked"] + statInterval < now:
        #sys.stderr.write(f"@@@ getReverseProxyRoutesDict: STAT elapsed = {now - reverseProxyRoutes['lastchecked']}\n")
        reverseProxyRoutes["lastchecked"] = now
        timestamp_file = os.stat(path).st_mtime
    if dict is None or timestamp < timestamp_file:
        dict = loadReverseProxyRoutesDict(path)
        reverseProxyRoutes["dict"] = dict
        reverseProxyRoutes["timestamp"] = timestamp_file  
    #sys.stderr.write(f"@@@ getReverseProxyRoutesDict: dict = {dict}\n")
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
