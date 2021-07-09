import aiohttp
import asyncio
from logging import getLogger, DEBUG, INFO, WARNING
from logging.handlers import SysLogHandler
from urllib.request import Request, urlopen

handler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL7)
logger = getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(DEBUG)


class myAiohttp():

    def __init__(self):
        pass

    def send_request(self, method, url, request_hdr, input):
        try:
            req = Request(url, input, request_hdr, method=method)
            response = urlopen(req, timeout=86400)
            status = f"{response.status}"
            response_hdr = response.getheaders()
            logger.debug(f"@@@ SUCCESS {method} {url} STATUS {status}")

        except Exception as e:
            response = None
            status = f"{e.status}"
            response_hdr = [(k, e.response_hdr[k]) for k in e.response_hdr]
            logger.debug(f"@@@ EXCEPT {method} {url} STATUS {status}")

        return (response, status, response_hdr)


    def gen_respiter(self, response, write, chunked, xAccelBuffering, file_wrapper):
        if chunked or xAccelBuffering == False:
            wsgi_response_obj = write.__self__
            #logger.debug(f"@@@ UNBUFFERED READER")
            respiter = unbufferedReader(response)
            wsgi_response_obj.send_headers()
            wsgi_response_obj.chunked = False
        else:
            #logger.debug(f"@@@ FILE_WRAPPER")
            respiter = file_wrapper(response)
        return respiter


class unbufferedReader():
    def __init__(self, response):
        #logger.debug(f"@@@ UNBUFFERED READER __INIT__")
        self.response = response	## keep response
        amt = 8192			## buffer size
        self.b = bytearray(amt)

    def __iter__(self):
        #logger.debug(f"@@@ UNBUFFERED READER __ITER__")
        return self

    def __next__(self):
        #logger.debug(f"@@@ UNBUFFERED READER __NEXT__")
        try:
            n = self.response.fp.readinto1(self.b)
        except:
            raise StopIteration
        if n == 0:
            raise StopIteration
        data = bytes(self.b[:n])
        #logger.debug(f"@@@ UNBUFFERED READER n = {n} data = [{debug_dumps(data)}]")
        return data


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
