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
from resource_api.common.encoders import encode_resource, encode_file_metadata, encode_files, encode_creator, \
    encode_metadata

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


    def test_encoders_errors(self):
        self.assertRaises(TypeError, encode_file_metadata, '')
        self.assertRaises(TypeError, encode_files, '')
        self.assertRaises(TypeError, encode_creator, '')
        self.assertRaises(TypeError, encode_metadata, '')
        self.assertRaises(TypeError, encode_resource, '')

if __name__ == '__main__':
    unittest.main()
