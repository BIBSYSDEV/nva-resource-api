import http
import os
import sys

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
import random
import string
import unittest
import uuid

from resource_api.common.validator import validate_resource_insert, validate_resource_modify
from resource_api.common.constants import Constants
from resource_api.common.helpers import response
from resource_api.common.encoders import encode_resource, encode_file_metadata, encode_files, encode_creator, \
    encode_metadata
from resource_api.data.creator import Creator
from resource_api.data.file import File
from resource_api.data.file_metadata import FileMetadata
from resource_api.data.metadata import Metadata
from resource_api.data.resource import Resource
from resource_api.data.title import Title


class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def random_word(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def generate_mock_resource(self, time_created=None, time_modified=None, uuid=uuid.uuid4().__str__()):
        title_1 = Title('no', self.random_word(6))
        title_2 = Title('en', self.random_word(6))
        titles = {title_1.language_code: title_1.title, title_2.language_code: title_2.title}
        creator_one = Creator('AUTHORITY_IDENTIFIER_1')
        creator_two = Creator('AUTHORITY_IDENTIFIER_2')
        creators = [creator_one, creator_two]
        metadata = Metadata(creators, 'https://hdl.handle.net/11250.1/1', 'LICENSE_IDENTIFIER_1', '2019', 'Unit',
                            titles, 'text')
        file_metadata_1 = FileMetadata(self.random_word(6) + '.txt', 'text/plain', '595f44fec1e92a71d3e9e77456ba80d1',
                                       '987654321')
        file_metadata_2 = FileMetadata(self.random_word(6) + '.pdf', 'application/pdf',
                                       '71f920fa275127a7b60fa4d4d41432a3', '123456789')
        file_1 = File('FILE_IDENTIFIER_1', file_metadata_1)
        file_2 = File('FILE_IDENTIFIER_2', file_metadata_2)
        files = dict()
        files[file_1.identifier] = file_1.file_metadata
        files[file_2.identifier] = file_2.file_metadata
        return Resource(uuid, time_modified, time_created, metadata, files, 'owner@unit.no')

    def test_resource(self):
        resource = self.generate_mock_resource('2019-11-02T08:46:14.464755+00:00', '2019-11-02T08:46:14.464755+00:00',
                                               'ebf20333-35a5-4a06-9c58-68ea688a9a8b')
        Resource.from_dict(resource.__dict__)

    def test_helper_response(self):
        _response = response(http.HTTPStatus.OK, 'message')
        self.assertEqual(_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK)

    def test_resource_validator_insert(self):
        resource = self.generate_mock_resource('2019-11-02T08:46:14.464755+00:00', '2019-11-02T08:46:14.464755+00:00',
                                               'ebf20333-35a5-4a06-9c58-68ea688a9a8b')
        resource_dict = Resource.from_dict(resource.__dict__)
        self.assertRaises(ValueError, validate_resource_insert, resource_dict)
        resource_dict.resource_identifier = None
        resource_dict.metadata = {}
        resource_dict.files = 'invalid_type'
        self.assertRaises(ValueError, validate_resource_insert, resource_dict)
        resource_dict.metadata = 'invalid_type'
        self.assertRaises(ValueError, validate_resource_insert, resource_dict)
        resource_dict.owner = None
        self.assertRaises(ValueError, validate_resource_insert, resource_dict)
        resource_dict.files = None
        self.assertRaises(ValueError, validate_resource_insert, resource_dict)
        resource_dict.metadata = None
        self.assertRaises(ValueError, validate_resource_insert, resource_dict)

    def test_resource_validator_modify(self):
        resource = self.generate_mock_resource('2019-11-02T08:46:14.464755+00:00', '2019-11-02T08:46:14.464755+00:00',
                                               'ebf20333-35a5-4a06-9c58-68ea688a9a8b')
        resource_dict = Resource.from_dict(resource.__dict__)
        resource_dict.metadata = {}
        resource_dict.files = 'invalid_type'
        self.assertRaises(ValueError, validate_resource_modify, resource_dict)
        resource_dict.metadata = 'invalid_type'
        self.assertRaises(ValueError, validate_resource_modify, resource_dict)
        resource_dict.owner = None
        self.assertRaises(ValueError, validate_resource_modify, resource_dict)
        resource_dict.files = None
        self.assertRaises(ValueError, validate_resource_modify, resource_dict)
        resource_dict.metadata = None
        self.assertRaises(ValueError, validate_resource_modify, resource_dict)
        resource_dict.resource_identifier = None
        self.assertRaises(ValueError, validate_resource_modify, resource_dict)

    def test_encoders(self):
        resource = self.generate_mock_resource('2019-11-02T08:46:14.464755+00:00', '2019-11-02T08:46:14.464755+00:00',
                                               'ebf20333-35a5-4a06-9c58-68ea688a9a8b')
        encode_resource(resource)
        encode_metadata(resource.metadata)
        encode_files(resource.files)
        encode_file_metadata(resource.files['FILE_IDENTIFIER_1'])
        encode_resource(None)
        encode_metadata(None)
        encode_metadata(Metadata(None, None, None, None, None, None, None))
        encode_files(None)
        self.assertEqual(encode_metadata(Metadata(None, None, None, None, None, dict(), None)), {},
                         'Unexpected metadata')

    def test_encoders_errors(self):
        self.assertRaises(TypeError, encode_file_metadata, '')
        self.assertRaises(TypeError, encode_files, '')
        self.assertRaises(TypeError, encode_creator, '')
        self.assertRaises(TypeError, encode_metadata, '')
        self.assertRaises(TypeError, encode_resource, '')


if __name__ == '__main__':
    unittest.main()
