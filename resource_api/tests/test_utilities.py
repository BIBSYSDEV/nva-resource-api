import http
import os
import sys

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
import random
import string
import unittest

from resource_api.common.constants import Constants
from resource_api.common.helpers import response

class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def random_word(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def test_helper_response(self):
        _response = response(http.HTTPStatus.OK, 'message')
        self.assertEqual(_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK)

if __name__ == '__main__':
    unittest.main()
