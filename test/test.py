import os
import random
import string
import subprocess
import sys
import time
import unittest
from runminio import runminio
from s3client import Mys3client

class TestStringMethods(unittest.TestCase):

#    def aws(self, args):
#        return "ok\n"
#
#    def test_upper(self):
#        res = self.aws(["s3", "ls", "s3://"])
#        self.assertTrue(res.strip("\n").endswith("ok"))

    def test_create_bucet(self):
        bucket_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 24))
        e = self.s3.create_bucket(bucket_name)
        print("create bucket: e = {}".format(e))
        buckets = [e for e in self.s3.list_buckets() if e.get("Name") == bucket_name]
        print("buckets: {}".format(buckets))
        self.s3.delete_bucket(bucket_name)
        self.assertTrue(buckets)

    def setUp(self):
        self.minio_p = runminio()
        while True:
            line = self.minio_p.stdout.readline()
            if not line:
                return False
            line = line.decode()
            print("+ {}".format(line.strip('\n')))
            if line.startswith("Object"):
                break
        print("setUp: minio pid = {}".format(self.minio_p))
        self.s3 = Mys3client()

    def tearDown(self):
        del self.s3
        self.minio_p.stdout.close()
        print("tearDown: kill -TERM {}".format(self.minio_p.pid))
        self.minio_p.terminate()
        self.minio_p.wait()

def main():
    unittest.main()

if __name__ == "__main__":
    main()
