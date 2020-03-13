import http
import simplejson as json
import os
import sys
import unittest
from unittest import mock

import boto3
from moto import mock_dynamodb2

from resource_api.common.constants import Constants
from resource_api.common.http_constants import HttpConstants
from resource_api.tests.test_constants import TestConstants

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))


def remove_mock_database(dynamodb):
    dynamodb.Table(os.environ[Constants.env_var_table_name()]).delete()


def generate_mock_event(http_method, resource):
    body_value = json.dumps(resource)
    return {
        Constants.event_http_method(): http_method,
        Constants.event_body(): body_value,
        Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): resource[Constants.event_identifier()]}
    }

@mock_dynamodb2
class TestHandlerCase(unittest.TestCase):
    EXISTING_RESOURCE_IDENTIFIER = '4d96e658-c2e0-4f23-9f1d-ccae0c770ecd'

    def setUp(self):
        """Mocked AWS Credentials for moto."""
        os.environ[TestConstants.env_var_aws_access_key_id()] = 'testing'
        os.environ[TestConstants.env_var_aws_secret_access_key()] = 'testing'
        os.environ[TestConstants.env_var_aws_security_token()] = 'testing'
        os.environ[TestConstants.env_var_aws_session_token()] = 'testing'

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
    def test_handler_modify_resource(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource()
        event = generate_mock_event(HttpConstants.http_method_put(), resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.response_status_code()], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_unknown_resource_identifier_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource()
        resource['identifier'] = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
        event = generate_mock_event(HttpConstants.http_method_put(), resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
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
        resource = self.generate_mock_resource()
        event = generate_mock_event('INVALID_HTTP_METHOD', resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_http_method_in_event_body(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        request_handler = RequestHandler(dynamodb)
        resource = self.generate_mock_resource()
        event = generate_mock_event(None, resource)
        handler_modify_response = request_handler.handler(event, None)
        self.assertEqual(handler_modify_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_missing_event(self):
        from resource_api.modify_resource import app
        dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        handler_modify_response = app.handler(None, None)
        self.assertEqual(handler_modify_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app(self):
        from resource_api.modify_resource import app
        event = {
            "body": "{}"
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
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
        self.assertEqual(handler_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_event_invalid_json_in_body(self):
        from resource_api.modify_resource import app
        event = {
            "httpMethod": "PUT",
            "body": "asdf",
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): self.EXISTING_RESOURCE_IDENTIFIER}
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_region(self):
        del os.environ['REGION']
        from resource_api.modify_resource import app
        app.clear_dynamodb()
        resource = self.generate_mock_resource()
        _event = generate_mock_event(HttpConstants.http_method_put(), resource)
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.response_status_code()], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_table(self):
        del os.environ['TABLE_NAME']
        from resource_api.modify_resource import app
        app.clear_dynamodb()
        resource = self.generate_mock_resource()
        _event = generate_mock_event(HttpConstants.http_method_put(), resource)

        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.response_status_code()], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_missing_resource_identifier(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.event_http_method(): HttpConstants.http_method_put(),
            Constants.event_path_parameters(): {}
        }

        _handler_modify_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_modify_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_modify_resource_missing_event(self):
        from resource_api.modify_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _handler_modify_response = _request_handler.handler(None, None)

        self.assertEqual(_handler_modify_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)
