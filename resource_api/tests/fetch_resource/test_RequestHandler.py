import os
import sys
import json
from unittest import mock

import http
import unittest

import boto3
from moto import mock_dynamodb2

from resource_api.common.http_constants import HttpConstants
from resource_api.common.constants import Constants
from resource_api.tests.test_constants import TestConstants


testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))


def remove_mock_database(dynamodb):
    dynamodb.Table(os.environ[Constants.env_var_table_name()]).delete()


@mock_dynamodb2
class TestHandlerCase(unittest.TestCase):
    EXISTING_RESOURCE_IDENTIFIER = 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'

    def setUp(self):
        """Mocked AWS Credentials for moto."""
        os.environ[TestConstants.env_var_aws_access_key_id()] = 'testing'
        os.environ[TestConstants.env_var_aws_secret_access_key()] = 'testing'
        os.environ[TestConstants.env_var_aws_security_token()] = 'testing'
        os.environ[TestConstants.env_var_aws_session_token()] = 'testing'

    def tearDown(self):
        pass

    def setup_mock_database(self, region, table_name):
        _dynamodb = boto3.resource('dynamodb', region_name=region)
        _table_connection = _dynamodb.create_table(TableName=table_name,
                                                   KeySchema=[
                                                       {'AttributeName': 'identifier',
                                                        'KeyType': 'HASH'},
                                                       {'AttributeName': 'modifiedDate',
                                                        'KeyType': 'RANGE'}],
                                                   AttributeDefinitions=[
                                                       {'AttributeName': 'identifier',
                                                        'AttributeType': 'S'},
                                                       {'AttributeName': 'modifiedDate',
                                                        'AttributeType': 'S'}],
                                                   ProvisionedThroughput={'ReadCapacityUnits': 1,
                                                                          'WriteCapacityUnits': 1})
        _table_connection.put_item(
            Item={
                'identifier': self.EXISTING_RESOURCE_IDENTIFIER,
                'modifiedDate': '2019-10-24T12:57:02.655994Z',
                'createdDate': '2019-10-24T12:57:02.655994Z',
                'entityDescription': {
                    'titles': {
                        'no': 'En tittel'
                    }
                }
            }
        )
        return _dynamodb

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app(self):
        from resource_api.fetch_resource import app
        dynamodb = self.setup_mock_database('eu-west-1', 'testing')
        _event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): self.EXISTING_RESOURCE_IDENTIFIER},
        }
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.response_status_code()], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        _ddb_response = json.loads(_handler_response[Constants.event_body()])
        self.assertEqual(_ddb_response[Constants.ddb_response_attribute_name_count()], 1,
                         'Count is not 1')
        remove_mock_database(dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_event_invalid_json_in_body(self):
        from resource_api.fetch_resource import app
        event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_body(): "asdf"
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_region(self):
        del os.environ['REGION']
        from resource_api.fetch_resource import app
        _event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): self.EXISTING_RESOURCE_IDENTIFIER},
        }
        app._dynamodb = None
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.response_status_code()], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_table(self):
        del os.environ['TABLE_NAME']
        from resource_api.fetch_resource import app
        _event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): ''},
        }

        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.response_status_code()], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    def test_handler_retrieve_resource_missing_event(self):
        from resource_api.fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        _request_handler = RequestHandler(_dynamodb)

        _handler_retrieve_response = _request_handler.handler(None, None)

        self.assertEqual(_handler_retrieve_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource(self):
        from resource_api.fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.response_status_code()], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource_wrong_http_method(self):
        from resource_api.fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.event_http_method(): 'POST',
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource_not_found(self):
        from resource_api.fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_path_parameters(): {Constants.event_path_parameter_identifier(): 'fbf20333-35a5-4a06-9c58-68ea688a9a8b'}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.response_status_code()], http.HTTPStatus.NOT_FOUND,
                         'HTTP Status code not 404')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource_missing_resource_identifier(self):
        from resource_api.fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.event_http_method(): HttpConstants.http_method_get(),
            Constants.event_path_parameters(): {}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.response_status_code()], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)
