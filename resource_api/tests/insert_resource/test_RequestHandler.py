import http
import json
import os
import random
import string
import sys
import unittest
from unittest import mock

import boto3
from boto3.dynamodb.conditions import Key
from resource_api.common.http_constants import HttpConstants
from resource_api.common.constants import Constants
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
    body_value = json.dumps(resource)
    return {
        Constants.EVENT_HTTP_METHOD: http_method,
        Constants.EVENT_BODY: body_value,
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
                                                 KeySchema=[{'AttributeName': 'identifier', 'KeyType': 'HASH'},
                                                            {'AttributeName': 'modifiedDate', 'KeyType': 'RANGE'}],
                                                 AttributeDefinitions=[
                                                     {'AttributeName': 'identifier', 'AttributeType': 'S'},
                                                     {'AttributeName': 'modifiedDate', 'AttributeType': 'S'}],
                                                 ProvisionedThroughput={'ReadCapacityUnits': 1,
                                                                        'WriteCapacityUnits': 1})
        table_connection.put_item(
            Item={
                'identifier': self.EXISTING_RESOURCE_IDENTIFIER,
                'modifiedDate': '2019-11-02T08:46:14.464755+00:00',
                'createdDate': '2019-11-02T08:46:14.464755+00:00',
                'entityDescription': {
                    'titles': {
                        'no': 'En tittel'
                    }
                },
                'fileSet': {},
                'owner': 'owner@unit.no'
            }
        )

        return dynamodb

    def random_word(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def generate_mock_resource(self):
        return json.loads('''
        {
          "createdDate": "2020-01-29T14:32:43.770Z",
          "status": "New",
          "modifiedDate": "2020-01-29T14:32:43.770Z",
          "owner": "pytest",
          "identifier": "4d96e658-c2e0-4f23-9f1d-ccae0c770ecd",
          "entityDescription": {
            "type": "JournalArticle",
            "titles": {
              "en": "Toward unique identifiers"
            },
            "date": {
              "year": "1999"
            },
            "contributors": [
              {
                "name": "Paskin, N.",
                "nameType": "Personal",
                "sequence": 0
              }
            ]
          }
        }
        ''')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_insert_resource(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource()
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)
        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.CREATED,
                         'HTTP Status code not 201')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_unknown_http_method_in_event(self):
        from resource_api.insert_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource()
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
        resource = self.generate_mock_resource()
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

        resource = self.generate_mock_resource()
        event = generate_mock_event(HttpConstants.HTTP_METHOD_POST, resource)
        handler_insert_response = request_handler.handler(event, None)

        resource_dict_from_json = json.loads(event[Constants.EVENT_BODY])
        resource_inserted = resource_dict_from_json

        self.assertEqual(handler_insert_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.CREATED,
                         'HTTP Status code not 201')

        resource_identifier = resource_inserted[Constants.EVENT_IDENTIFIER]

        query_results = request_handler.get_table_connection().query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_IDENTIFIER).eq(resource_identifier),
            ScanIndexForward=True
        )

        inserted_resource = query_results[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][0]
        self.assertIsNotNone(inserted_resource[Constants.DDB_FIELD_CREATED_DATE], 'Value not persisted as expected')
        self.assertIsNotNone(inserted_resource[Constants.DDB_FIELD_MODIFIED_DATE], 'Value not persisted as expected')
        self.assertIsNotNone(inserted_resource[Constants.DDB_FIELD_ENTITY_DESCRIPTION], 'Value not persisted as expected')
        self.assertEqual(inserted_resource[Constants.DDB_FIELD_MODIFIED_DATE],
                         inserted_resource[Constants.DDB_FIELD_CREATED_DATE],
                         'Value not persisted as expected')
        self.assertEqual(inserted_resource[Constants.DDB_FIELD_ENTITY_DESCRIPTION], resource_inserted['entityDescription'],
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
            Constants.EVENT_BODY: "{}"
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
            Constants.EVENT_BODY: "{}"
        }

        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')


if __name__ == '__main__':
    unittest.main()