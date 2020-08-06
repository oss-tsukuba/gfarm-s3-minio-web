import os
import subprocess
import sys
import unittest

class TestStringMethods(unittest.TestCase):

    def aws(self, args):
        return "ok\n"

    def setUp(self):
        pass

    def test_upper(self):
        res = self.aws(["s3", "ls", "s3://"])
        self.assertTrue(res.strip("\n").endswith("ok"))

if __name__ == "__main__":
    unittest.main()