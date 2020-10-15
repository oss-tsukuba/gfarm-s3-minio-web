import filecmp
import os
import random
import string
import subprocess
import sys
import tempfile
import time
import unittest
from runminio import runminio
from s3client import Mys3client

class TestS3(unittest.TestCase):

    ## create bucket && delete bucket
    def test_create_bucket(self):
        bucket = random_s3_name()
        e = self.s3.create_bucket(bucket)
        self.assertIsNone(e)
        buckets = [e for e in self.s3.list_buckets() if e.get("Name") == bucket]
        print("buckets: {}".format(buckets))
        self.s3.delete_bucket(bucket)
        self.assertNotEqual(buckets, [])

    ## send file && receive file
    def test_send_recv_8(self):
        e = up_down_n_cmp_sz(self.s3, 8)
        self.assertIsNone(e)

    def test_send_recv_32(self):
        e = up_down_n_cmp_sz(self.s3, 32)
        self.assertIsNone(e)

    def test_send_recv_128(self):
        e = up_down_n_cmp_sz(self.s3, 128)
        self.assertIsNone(e)

    def test_send_recv_512(self):
        e = up_down_n_cmp_sz(self.s3, 512)
        self.assertIsNone(e)

    ## list object(s)
    def test_list_object(self):
        e = list_object(self.s3)
        self.assertIsNone(e)

    ## list prefixed object(s)
    def test_list_prefixed_object(self):
        e = list_object(self.s3, prefixed = True)
        self.assertIsNone(e)

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

def up_down_n_cmp_sz(s3, size):
    now = time.time()
    start = now

    with tempfile.TemporaryDirectory(dir = ".") as tmpdirname:
        print("temporary directory {}".format(tmpdirname))

        bucket = random_s3_name()
        with s3.withBucket(bucket) as b:
            print("bucket name {}".format(b.name)) ## b.name == bucket
    
            with tempfile.NamedTemporaryFile(dir = tmpdirname) as sendfile:
                print("created temporary file: {}".format(sendfile.name))
        
                with tempfile.NamedTemporaryFile(dir = tmpdirname) as recvfile:
                    print("created temporary file: {}".format(recvfile.name))
        
                    e = createFileM(sendfile.name, size, force = True)
                    if e:
                        return e
        
                    key = random_s3_name()
        
                    e = send_recv_cmp(s3, sendfile.name, bucket, key, recvfile.name)
        
                    d = s3.delete_object(bucket, key)
                    if d and e is not None:
                        e = d
                    now = time.time()
                    print("@@@ {} ({})".format(myformat(now), now - start))
                    return e

def send_recv_cmp(s3, sendfile, bucket, key, recvfile):

    with open(sendfile, "rb") as f:
        e = s3.upload_fileobj(f, bucket, key)
        if e:
            return e

    with open(recvfile, "wb") as f:
        e = s3.download_fileobj(f, bucket, key)
        if e:
            return e

    if not filecmp.cmp(sendfile, recvfile, shallow = False):
        return "filecmp.cmp: {} {} mismatch".format(sendfile, recvfile)

    return None

def list_object(s3, prefixed = False):
    with tempfile.TemporaryDirectory(dir = ".") as tmpdirname:
        print("temporary directory {}".format(tmpdirname))

        bucket = random_s3_name()
        with s3.withBucket(bucket) as b:
            print("bucket name {}".format(b.name)) ## b.name == bucket
    
            with tempfile.NamedTemporaryFile(dir = tmpdirname) as sendfile:
                print("created temporary file: {}".format(sendfile.name))
        
                with open(sendfile.name, "wb") as f:
                    e = None

                    f.write(os.urandom(64))
        
                    key1 = random_s3_name()
                    key2 = random_s3_name()

                    if prefixed:
                        key1 = key1[:3] + "/" + key1[3 + 1:]
                        key2 = key2[:3] + "/" + key2[3 + 1:]
        
                    d = s3.upload_file(sendfile.name, bucket, key1)
                    if d and e is not None:
                        e = d
                    d = s3.upload_file(sendfile.name, bucket, key2)
                    if d and e is not None:
                        e = d

                    o = s3.list_objects(bucket)

                    print("{}".format(o))

                    p = [e.get("Key", None) for e in o]
                    q = [key1, key2]
                    p.sort()
                    q.sort()

                    print("{}".format(p))
                    print("{}".format(q))
                    if not p == q:
                        e = "object listing mismatch"

                    d = s3.delete_object(bucket, key1)
                    if d and e is not None:
                        e = d
                    d = s3.delete_object(bucket, key2)
                    if d and e is not None:
                        e = d
                    return e

def random_s3_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k = 24))

def createFileM(path, sz, force = False):
    if not force and os.path.isfile(path):
        return "file exists {}".format(path)
    print("createFileM({}, {})".format(path, sz))
    with open(path, "wb") as f:
       for m in range(sz):
           f.write(os.urandom(1 * 1024 * 1024))
    return None

def myformat(t):
    i = time.strftime('%Y%m%dT%H%M%S', time.gmtime(t))
    f = (int)((t % 1) * 1000000)
    return "{}.{:06d}Z".format(i, f)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
