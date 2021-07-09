from logging import getLogger, DEBUG, INFO, WARNING
from logging.handlers import SysLogHandler
import requests

handler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL7)
logger = getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(DEBUG)


class myRequests():

    def __init__(self):
        pass

    def send_request(self, method, url, request_hdr, input):
        try:
            logger.debug(f"@@@ START requests.{method}")
            if method == "GET":
                response = requests.get(url, headers=request_hdr)
            elif method == "HEAD":
                response = requests.head(url, headers=request_hdr)
            elif method == "DELETE":
                response = requests.delete(url, headers=request_hdr)
            elif method == "PUT":
                input = input.read()
                response = requests.put(url, headers=request_hdr, data=input)
            elif method == "POST":
                input = input.read()
                response = requests.post(url, headers=request_hdr, data=input)
            else:
                logger.error(f"@@@ ERROR: unsupported method: {method}")
                raise Exception("unsupported method")
            logger.debug(f"@@@ END requests.{method}")
            status = response.status_code
            status = f"{status}"
            response_hdr = response.headers
            response_hdr = [(k, response_hdr[k]) for k in response_hdr]
            logger.debug(f"@@@ SUCCESS {method} {url} STATUS {status}")

        except Exception as e:
            response = None
            status = "500"
            response_hdr = []
            logger.debug(f"@@@ EXCEPT {method} {url} STATUS {status}")

        return (response, status, response_hdr)

    def gen_respiter(self, response, write, chunked, xAccelBuffering, file_wrapper):
        if chunked or xAccelBuffering == False:
            logger.debug(f"@@@ RESPONSE response {type(response)}")
            logger.debug(f"@@@ RESPONSE response.content {type(response.content)}")
            logger.debug(f"@@@ RESPONSE unbufferedReader(response)")
            respiter = unbufferedReader(response)
        else:
            #respiter = file_wrapper(response.content)
            respiter = [response.content]

        logger.debug(f"@@@ CONTENT = {debug_dumps(response.content)}")
        return respiter


class unbufferedReader():
    def __init__(self, response):
        #logger.debug(f"@@@ UNBUFFERED READER __INIT__")
        self.response = response	## keep response
        #amt = 8192			## buffer size
        #self.b = bytearray(amt)

    def __iter__(self):
        #logger.debug(f"@@@ UNBUFFERED READER __ITER__")
        return self

    def __next__(self):
        #logger.debug(f"@@@ UNBUFFERED READER __NEXT__")


        logger.debug(f"@@@ UNBUFFERED READER __NEXT__")
        try:
            logger.debug(f"@@@ UNBUFFERED READER READ_CHUNKED")
            b = self.res.raw.read_chunked()
        except:
            raise StopIteration
        logger.debug(f"@@@ UNBUFFERED READER b = {type(b)}")
        n = len(b)
        logger.debug(f"@@@ UNBUFFERED READER n = {n} b = [{debug_dumps(b)}]")
        if n == 0:
            raise StopIteration
        #buf = bytes(self.b[:n])
        #logger.debug(f"@@@ UNBUFFERED READER n = {n} buf = [{debug_dumps(buf)}]")
        #return buf
        return b


def debug_dumps(s):
    r = ""
    for c in s:
        if ord(' ') <= c and c <= ord('~'):
            r += f"{chr(c)}"
        elif c == ord('\t'):
            r += "\\t"
        elif c == ord('\n'):
            r += "\\n"
        elif c == ord('\r'):
            r += "\\r"
        elif c == ord('\\'):
            r += "\\\\"
        else:
            r += "\\{0:03o}".format(c)
    return r
