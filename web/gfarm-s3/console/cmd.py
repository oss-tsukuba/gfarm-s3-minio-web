import json
import locale
import os
from subprocess import Popen, PIPE, DEVNULL
import time
import threading
import urllib.parse
from django.utils.translation import gettext as _

from contextlib import contextmanager

from gfarms3 import conf

logger = conf.get_logger(__name__)

def gfarm_s3_login(action, username, passwd, stdin = None, authenticated = None, bucket = None, remote_addr = None):
    #logger.debug(f"gfarm_s3_login")
    GFARM_S3_BIN = conf.get_str("GFARM_S3_BIN")
    args = [action, username, passwd]
    if authenticated is not None:
        args = ["--authenticated", authenticated] + args
    if bucket is not None:
        args = ["--bucket", bucket] + args
    if remote_addr is not None:
        args = ["--remote_addr", remote_addr] + args
    gfarm_s3_login_bin = os.path.join(GFARM_S3_BIN, "gfarm-s3-login")
    return Popen([gfarm_s3_login_bin] + args, stdin = stdin, stdout = PIPE, stderr = PIPE, env = {})

def decode(s):
    if isinstance(s, bytes):
        return s.decode()
    return s

def _communicate(p, name, input=DEVNULL):
    try:
        stdout, stderr = p.communicate(input=input)
        p.wait()
        if stderr:
            stderr = decode(stderr)
            if p.returncode == 0:
                for l in stderr.splitlines():
                    logger.info(f"{l}")
            else:
                for l in stderr.splitlines():
                    logger.error(f"{l}")
        return p.returncode, decode(stdout)
    except Exception as e:
        logger.error(f"{name}: {e}")
        return -1, f"{e}"

def cmd(action, username, passwd, authenticated = None, remote_addr = None, lang = None):
    try:
        p = gfarm_s3_login(action, username, passwd, authenticated = authenticated, remote_addr = remote_addr)
    except Exception as e:
        logger.error(f"cmd: ERROR 1: {e}")
        return {"status": "ERROR 1", "reason": "Popen failed"}

    retcode, stdout = _communicate(p, f"cmd:{action}")
    if retcode != 0:
        return {"status": "ERROR 2",
                "reason": f"action = {action}, retcode = {retcode}, {stdout}  (Please contact administrator)"}

    try:
        result = json.loads(decode(stdout).strip())
    except Exception as e:
        logger.error(f"cmd: ERROR 4 (parse JSON): {e} [{stdout}]")
        return {"status": "ERROR 4", "reason": f"{e}"}
    if "expiration_date" in result.keys():
        result["expiration_date_calendar_datetime"] = myctime(result["expiration_date"], lang)
    return result

def get_bucket_list(username):
    try:
        p = gfarm_s3_login("gfls", username, "", authenticated = "unspecified")
    except Exception as e:
        logger.error(f"get_bucket_list: exception: {e}")
        return None
    retcode, stdout = _communicate(p, "get_bucket_list")
    if retcode != 0:
        return None
    return split_lines(decode(stdout))

def get_bucket_acl(username, bucket):
    try:
        p = gfarm_s3_login("gfgetfacl", username, "", authenticated = "unspecified", bucket = bucket)
    except Exception as e:
        logger.error(f"get_bucket_acl: exception: {e}")
        return None
    retcode, stdout = _communicate(p, "get_bucket_acl")
    if retcode != 0:
        return None
    #logger.debug("GET_BUCKET_ACL: [{}]".format(decode(stdout) + "\n"))
    return split_lines(decode(stdout))

def need_default(s):
    return (s.startswith("group:") or s.startswith("user:")) and ("::" not in s)

def rewrite_any(s):
    if s.startswith("group::"):
        return "group::---"
    if s.startswith("other::"):
        return "other::---"
    return s

def is_fixed_entry(s):
    if s.startswith("#") or s.startswith("default:"):
        return False
    return "::" in s or s.startswith("mask:")

#def is_debug_entry(s):
#    return "77777" in s or "OTHER" in s

def fix_acl_1(acl):
    acl = [rewrite_any(e) for e in acl if is_fixed_entry(e)]
    return acl

def fix_acl_2(acl):
    #acl = [e for e in acl if not is_debug_entry(e)]
    #logger.debug("acl: {}".format(acl))
    oth = [e for e in acl if e.startswith("gfarms3webui:OTHER:")][0]
    grp = [e for e in acl if e.startswith("gfarms3webui:GROUP:")][0]
    acl = [e for e in acl if not e.startswith("gfarms3webui:")]
    #logger.debug("acl: {}".format(acl))
    #logger.debug("oth: {}".format(oth))
    default = ["default:" + e for e in acl if need_default(e)]
    acl = acl + grp_to_aclentry(grp)
    acl = acl + oth_to_aclentry(oth)

    return acl + default

def grp_to_aclentry(grp):
    perm = grp.split(':')[2]
    return go_aclentry("group", perm)

def oth_to_aclentry(oth):
    perm = oth.split(':')[2]
    return go_aclentry("other", perm)

def go_aclentry(object, perm):
    if perm == "rwx":
        return [object + "::rwx", "default:" + object + "::rwx"]
    elif perm == "r-x":
        return [object + "::r-x", "default:" + object + "::r-x"]
    else:
        return [object + "::---", "default:" + object + "::---"]

def set_bucket_acl(username, bucket, acl_1, acl_2):
    #logger.debug("bucket: {}".format(bucket))
    #logger.debug("acl_1: {}".format(acl_1))
    #logger.debug("acl_2: {}".format(acl_2))
    acl = "\n".join(fix_acl_1(acl_1) + fix_acl_2(acl_2)) + "\n"
    #logger.debug("acl_fixed: {}".format(acl))
    try:
        p = gfarm_s3_login("gfsetfacl", username, "", authenticated = "unspecified", bucket = bucket, stdin = PIPE)
    except Exception as e:
        logger.error(f"set_bucket_acl: exception: {e}")
        return None
    retcode, stdout = _communicate(p, "set_bucket_acl", input=acl.encode())
    if retcode != 0:
        return None
    return decode(stdout)

def get_group_list(username):
    try:
        p = gfarm_s3_login("gfgroup", username, "", authenticated = "unspecified")
    except Exception as e:
        logger.error(f"get_group_list: exception: {e}")
        return None
    retcode, stdout = _communicate(p, "get_group_list")
    if retcode != 0:
        return None
    return split_lines(decode(stdout))

def get_user_list(username):
    try:
        p = gfarm_s3_login("gfuser", username, "", authenticated = "unspecified")
    except Exception as e:
        logger.error(f"get_user_list: exception: {e}")
        return None
    retcode, stdout = _communicate(p, "get_user_list")
    if retcode != 0:
        return None
    return split_lines(decode(stdout))

def split_lines(s):
    return [e.strip() for e in s.split('\n') if e.strip() != ""]

def get_groups_users_list(username):
    groups = get_group_list(username)
    groups.sort()
    groups = [{"id": "group:" + e, "text": "group:" + e} for e in groups]
    users = get_user_list(username)
    users.sort()
    users = [{"id": "user:" + user_id(e), "text": "user:" + pretty_name(e)} for e in users]
    return (groups, users)

def user_id(s):
    ss = s.split(':')
    return ss[0]

def pretty_name(s):
    ss = s.split(':')
    uu = ss[1].split('[')
    t = urllib.parse.unquote(uu[0]) + "(" + ss[0] + ")"
    return t

LOCALE_LOCK = threading.Lock()

@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        except Exception:
            yield locale.setlocale(locale.LC_ALL, saved)

def myctime(sec, lang):
    lt = time.localtime(sec)
    format = _('ctime_format')
    if lang == "ja":
        l = "ja_JP.UTF-8"
    else:
        l = "C"
    with setlocale(l):
       return time.strftime(format, lt)
