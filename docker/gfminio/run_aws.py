from subprocess import Popen, PIPE
import sys

args = sys.argv.copy()
args.pop(0)

cmd = ["aws"] + args

with Popen(cmd, stderr=PIPE) as b:
    try:
        (out, err) = b.communicate()
        for e in err.splitlines():
            e = e.decode()
            if e.find("InsecureRequestWarning:") == -1:
                print(f"{e}")
        status = b.wait()
        exit(status)
    except Exception as e:
        print(e)
        exit(1)
