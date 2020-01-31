import os
import sys
from unittest import mock

import http
import json
import random
import string
import unittest
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from moto import mock_dynamodb2

from resource_api.common.constants import Constants
from resource_api.common.http_constants import HttpConstants
from resource_api.common.encoders import encode_resource
from resource_api.common.helpers import remove_none_values
from resource_api.data.creator import Creator
from resource_api.data.file import File
from resource_api.data.file_metadata import FileMetadata
from resource_api.data.metadata import Metadata
from resource_api.data.resource import Resource
from resource_api.data.title import Title

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))


def unittest_lambda_handler(event, context):
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestHandlerCase))


def remove_mock_database(dynamodb):
    dynamodb.Table(os.environ[Constants.ENV_VAR_TABLE_NAME]).delete()


def generate_mock_event(http_method, resource):
    body = Body(resource)
    body_value = json.dumps(body, default=encode_body)
    return {
        'httpMethod': http_method,
        'body': body_value
    }


@mock_dynamodb2
class TestHandlerCase(unittest.TestCase):
    EXISTING_RESOURCE_IDENTIFIER = 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'
    EXISTING_RESOURCE_CREATED_DATE = '2019-11-02T08:46:14.464755+00:00'
    EXISTING_RESOURCE_MODIFIED_DATE = '2019-11-02T08:46:14.464755+00:00'
    EXISTING_RESOURCE_METADATA = {
        'metadata': {
            'titles': {
                'no': 'En tittel'
            }
        }
    }
    EXISTING_RESOURCE_IDENTIFIER_MISSING_CREATED_DATE = 'acf20333-35a5-4a06-9c58-68ea688a9a9c'

    def setUp(self):
        """Mocked AWS Credentials for moto."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'

    def tearDown(self):
        pass

    def setup_mock_database(self, region, table_name):
        dynamodb = boto3.resource('dynamodb', region_name=region)
        table_connection = dynamodb.create_table(TableName=table_name,
                                                 KeySchema=[{'AttributeName': 'resource_identifier', 'KeyType': 'HASH'},
                                                            {'AttributeName': 'modifiedDate', 'KeyType': 'RANGE'}],
                                                 AttributeDefinitions=[
                                                     {'AttributeName': 'resource_identifier', 'AttributeType': 'S'},
                                                     {'AttributeName': 'modifiedDate', 'AttributeType': 'S'}],
                                                 ProvisionedThroughput={'ReadCapacityUnits': 1,
                                                                        'WriteCapacityUnits': 1})
        table_connection.put_item(
            Item={
                'resource_identifier': self.EXISTING_RESOURCE_IDENTIFIER,
                'modifiedDate': self.EXISTING_RESOURCE_MODIFIED_DATE,
                'createdDate': self.EXISTING_RESOURCE_CREATED_DATE,
                'metadata': {
                    'titles': {
                        'no': 'En tittel'
                    }
                },
                'files': {},
                'owner': 'owner@unit.no'
            }
        )

        table_connection.put_item(
            Item={
                'resource_identifier': self.EXISTING_RESOURCE_IDENTIFIER_MISSING_CREATED_DATE,
                'modifiedDate': '2019-11-04T08:46:14.464755+00:00',
                'metadata': {
                    'titles': {
                        'no': 'En tittel'
                    }
                },
                'files': {},
                'owner': 'owner@unit.no'
            }
        )

        return dynamodb

    def generate_random_resource(self, time_created, time_modified=None, uuid=uuid.uuid4().__str__()):
        if time_modified is None:
            time_modified = time_created
        return {
            'resource_identifier': uuid,
            'modifiedDate': time_modified,
            'createdDate': time_created,
            'metadata': {
                'titles': {
                    'no': self.random_word(6)
                }
            },
            'files': {},
            'owner': 'owner@unit.no'
        }

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

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_missing_resource_identifier(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        resource.resource_identifier = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_missing_resource_metadata_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        resource.metadata = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_missing_resource_owner_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        resource.owner = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'}, clear=True)
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'}, clear=True)
    def test_handler_modify_resource_missing_resource_files_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        resource.files = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_empty_resource_metadata_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        resource.metadata = Metadata(None, None, None, None, None, None)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_invalid_resource_metadata_type_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "PUT",
            "body": "{\"resource\": {\"resource_identifier\": "
                    "\"ebf20333-35a5-4a06-9c58-68ea688a9a8b\", \"owner\": \"owner@unit.no\", \"files\": {}, \"metadata\": \"invalid type\"}}"
        }
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        self.assertEqual(handler_modify_response[Constants.RESPONSE_BODY],
                         'Resource with identifier ebf20333-35a5-4a06-9c58-68ea688a9a8b has invalid attribute type for metadata',
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_invalid_files_type_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "PUT",
            "body": "{\"resource\": {\"resource_identifier\": "
                    "\"ebf20333-35a5-4a06-9c58-68ea688a9a8b\", \"owner\": \"owner@unit.no\", \"files\": \"invalid type\", \"metadata\": {}}}"
        }
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        self.assertEqual(handler_modify_response[Constants.RESPONSE_BODY],
                         'Resource with identifier ebf20333-35a5-4a06-9c58-68ea688a9a8b has invalid attribute type for files',
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_invalid_resource_identifier_field_json_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "PUT",
            "body": "{\"resource\": {\"identifer\": "
                    "\"ebf20333-35a5-4a06-9c58-68ea688a9a8b\", \"owner\": \"owner@unit.no\", \"files\": \"{}\", \"metadata\": {}}}"
        }
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_unexpected_resource_field_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "PUT",
            "body": "{\"resource\": {\"resource_identifier\": "
                    "\"ebf20333-35a5-4a06-9c58-68ea688a9a8b\", \"registrator\": \"owner@unit.no\", \"owner\": \"owner@unit.no\", \"files\": \"{}\", \"metadata\": {}}}"
        }
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_created_date_missing_in_existing_resource(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER_MISSING_CREATED_DATE)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        self.assertEqual(handler_modify_response[Constants.RESPONSE_BODY],
                         'Resource with identifier acf20333-35a5-4a06-9c58-68ea688a9a9c has no ' + Constants.DDB_FIELD_CREATED_DATE + ' in DB',
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_unknown_resource_identifier_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
        event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        self.assertEqual(handler_modify_response['body'],
                         'Resource with identifier xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx not found',
                         'Did not get expected error message')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_unknown_http_method_in_event(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        event = generate_mock_event('INVALID_HTTP_METHOD', resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_resource_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, None)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_http_method_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        event = generate_mock_event(None, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_event(self):
        from resource_api.modify_resource import app
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        handler_modify_response = app.handler(None, None)
        self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_modify_resource(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)

        for counter in range(2):
            resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
            event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
            handler_modify_response = request_handler.handler(event, None)

            self.assertEqual(handler_modify_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK,
                             'HTTP Status code not 200')

        query_results = request_handler.get_table_connection().query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_RESOURCE_IDENTIFIER).eq(
                self.EXISTING_RESOURCE_IDENTIFIER),
            ScanIndexForward=True
        )

        self.assertEqual(len(query_results[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS]), 3,
                         'Value not persisted as expected')

        initial_resource = query_results[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][0]
        first_modification_resource = query_results[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][1]
        second_modification_resource = query_results[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][2]

        resource_created_date = self.EXISTING_RESOURCE_CREATED_DATE

        self.assertEqual(first_modification_resource[Constants.DDB_FIELD_CREATED_DATE],
                         resource_created_date,
                         'Value not persisted as expected')
        self.assertEqual(second_modification_resource[Constants.DDB_FIELD_CREATED_DATE],
                         resource_created_date,
                         'Value not persisted as expected')
        self.assertEqual(self.EXISTING_RESOURCE_MODIFIED_DATE,
                         resource_created_date,
                         'Value not persisted as expected')
        self.assertNotEqual(first_modification_resource[Constants.DDB_FIELD_MODIFIED_DATE],
                            resource_created_date,
                            'Value not persisted as expected')
        self.assertNotEqual(second_modification_resource[Constants.DDB_FIELD_MODIFIED_DATE],
                            resource_created_date,
                            'Value not persisted as expected')
        self.assertNotEqual(first_modification_resource[Constants.DDB_FIELD_MODIFIED_DATE],
                            second_modification_resource[Constants.DDB_FIELD_MODIFIED_DATE],
                            'Value not persisted as expected')
        self.assertNotEqual(initial_resource[Constants.DDB_FIELD_METADATA],
                            first_modification_resource[Constants.DDB_FIELD_METADATA],
                            'Value not persisted as expected')
        self.assertNotEqual(initial_resource[Constants.DDB_FIELD_METADATA],
                            second_modification_resource[Constants.DDB_FIELD_METADATA],
                            'Value not persisted as expected')
        self.assertNotEqual(first_modification_resource[Constants.DDB_FIELD_METADATA],
                            second_modification_resource[Constants.DDB_FIELD_METADATA],
                            'Value not persisted as expected')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app(self):
        from resource_api.modify_resource import app
        event = {
            "body": "{}"
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_event_empty_body(self):
        from resource_api.modify_resource import app
        event = {
            "httpMethod": "PUT",
            "body": ""
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_event_invalid_json_in_body(self):
        from resource_api.modify_resource import app
        event = {
            "httpMethod": "PUT",
            "body": "{'fetch_resource': 'fetch_resource }"
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_region(self):
        del os.environ['REGION']
        from resource_api.modify_resource import app
        app.clear_dynamodb()
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        _event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_table(self):
        del os.environ['TABLE_NAME']
        from resource_api.modify_resource import app
        app.clear_dynamodb()
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        _event = generate_mock_event(HttpConstants.HTTP_METHOD_PUT, resource)

        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')


if __name__ == '__main__':
    unittest.main()


class Body:

    def __init__(self, resource: Resource):
        self.resource = resource


def encode_body(instance):
    if isinstance(instance, Body):
        temp_value = {
            Constants.JSON_ATTRIBUTE_NAME_RESOURCE: encode_resource(instance.resource)
        }
        return remove_none_values(temp_value)
    else:
        type_name = instance.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")
