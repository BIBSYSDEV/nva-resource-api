import http
import json
import os
import random
import string
import sys
import unittest
import uuid
from unittest import mock

import boto3
from boto3.dynamodb.conditions import Key
from resource_api.common.http_constants import HttpConstants
from resource_api.common.constants import Constants
from resource_api.common.encoders import encode_resource
from resource_api.common.helpers import remove_none_values
from resource_api.data.creator import Creator
from resource_api.data.file import File
from resource_api.data.file_metadata import FileMetadata
from resource_api.data.metadata import Metadata
from resource_api.data.resource import Resource
from resource_api.data.title import Title
from moto import mock_dynamodb2

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
                'modifiedDate': '2019-11-02T08:46:14.464755+00:00',
                'createdDate': '2019-11-02T08:46:14.464755+00:00',
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
    def test_handler_insert_resource(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, None)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.CREATED,
                         'HTTP Status code not 201')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_with_identifier(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource()
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_missing_resource_metadata(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, None)
        resource.metadata = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_missing_resource_files(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, None)
        resource.files = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_invalid_resource_metadata_type_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "POST",
            "body": "{\"resource\": {\"owner\": \"owner@unit.no\", \"files\": {}, \"metadata\": \"invalid type\"}}"
        }
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_invalid_resource_files_type_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "POST",
            "body": "{\"resource\": {\"owner\": \"owner@unit.no\", \"files\": \"invalid type\", \"metadata\": {}}}"
        }
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_missing_resource_owner_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, None)
        resource.owner = None
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_empty_resource_metadata_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, None)
        resource.metadata = Metadata(None, None, None, None, None, None)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.CREATED,
                         'HTTP Status code not 201')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource_invalid_resource_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = {
            "httpMethod": "POST",
            "body": "{\"resource\": {\"owners\": \"owner@unit.no\", \"files\": {}, \"metadata\": \"invalid type\"}}"
        }
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_unknown_http_method_in_event(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, self.EXISTING_RESOURCE_IDENTIFIER)
        event = generate_mock_event('INVALID_HTTP_METHOD', resource)
        handler_response = request_handler.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_resource_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, None)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_http_method_in_event_body(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource(None, None, None)
        event = generate_mock_event(None, resource)
        handler_response = request_handler.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_event(self):
        from resource_api.insert_resource import app
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        handler_insert_response = app.handler(None, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_insert_resource(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)

        resource = self.generate_mock_resource(None, None, None)
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)

        resource_dict_from_json = json.loads(event[Constants.EVENT_BODY]).get(Constants.JSON_ATTRIBUTE_NAME_RESOURCE)
        resource_inserted = Resource.from_dict(resource_dict_from_json)

        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.CREATED,
                         'HTTP Status code not 201')

        resource_identifier = json.loads(handler_insert_response[Constants.RESPONSE_BODY]).get('resource_identifier')

        query_results = request_handler.get_table_connection().query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_RESOURCE_IDENTIFIER).eq(resource_identifier),
            ScanIndexForward=True
        )

        inserted_resource = query_results[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][0]
        self.assertIsNotNone(inserted_resource[Constants.DDB_FIELD_CREATED_DATE], 'Value not persisted as expected')
        self.assertIsNotNone(inserted_resource[Constants.DDB_FIELD_MODIFIED_DATE], 'Value not persisted as expected')
        self.assertIsNotNone(inserted_resource[Constants.DDB_FIELD_METADATA], 'Value not persisted as expected')
        self.assertEqual(inserted_resource[Constants.DDB_FIELD_MODIFIED_DATE],
                         inserted_resource[Constants.DDB_FIELD_CREATED_DATE],
                         'Value not persisted as expected')
        self.assertEqual(inserted_resource[Constants.DDB_FIELD_METADATA], resource_inserted.metadata,
                         'Value not persisted as expected')
        remove_mock_database(dynamodb)

    @mock_dynamodb2
    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app(self):
        from resource_api.insert_resource import app
        event = {
            Constants.EVENT_BODY: "{}"
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_event_empty_body(self):
        from resource_api.insert_resource import app
        event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_POST,
            Constants.EVENT_BODY: ""
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_event_invalid_json_in_body(self):
        from resource_api.insert_resource import app
        event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_POST,
            Constants.EVENT_BODY: "asdf"
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_region(self):
        del os.environ['REGION']
        from resource_api.insert_resource import app
        app.clear_dynamodb()
        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_POST,
            Constants.EVENT_BODY: "{\"resource\": {}}"
        }
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_table(self):
        del os.environ['TABLE_NAME']
        from resource_api.insert_resource import app
        app.clear_dynamodb()
        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_POST,
            Constants.EVENT_BODY: "{\"resource\": {}}"
        }

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
