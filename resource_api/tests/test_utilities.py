import http
import os
import sys
from unittest import mock


testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
import unittest

from resource_api.common.constants import Constants
from resource_api.common.http_constants import HttpConstants
from resource_api.common.helpers import response

class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_helper_response(self):
        _response = response(http.HTTPStatus.OK, 'message')
        self.assertEqual(_response[Constants.response_status_code()], http.HTTPStatus.OK)

    @mock.patch.dict(os.environ, {'ALLOWED_ORIGIN': '*'})
    def test_helper_response_with_cors(self):
        _response = response(http.HTTPStatus.OK, 'message')
        self.assertEqual(_response[Constants.response_status_code()], http.HTTPStatus.OK)
        self.assertEqual(
            _response[Constants.response_headers()][HttpConstants.http_header_access_control_allow_origin()],
            '*'
        )


if __name__ == '__main__':
    unittest.main()
