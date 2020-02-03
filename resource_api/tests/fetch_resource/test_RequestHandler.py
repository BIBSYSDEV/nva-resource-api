import os
import sys
from unittest import mock

import http
import unittest

import boto3
from moto import mock_dynamodb2

from common.http_constants import HttpConstants
from common.constants import Constants

testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))


def unittest_lambda_handler(event, context):
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestHandlerCase))


def remove_mock_database(dynamodb):
    dynamodb.Table(os.environ[Constants.ENV_VAR_TABLE_NAME]).delete()


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

    @mock_dynamodb2
    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app(self):
        from fetch_resource import app
        _event = {}
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_region(self):
        del os.environ['REGION']
        from fetch_resource import app
        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_GET,
            Constants.EVENT_PATH_PARAMETERS: {Constants.EVENT_PATH_PARAMETER_IDENTIFIER: self.EXISTING_RESOURCE_IDENTIFIER},
        }
        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_app_missing_env_table(self):
        del os.environ['TABLE_NAME']
        from fetch_resource import app
        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_GET,
            Constants.EVENT_PATH_PARAMETERS: {Constants.EVENT_PATH_PARAMETER_IDENTIFIER: ''},
        }

        _handler_response = app.handler(_event, None)
        self.assertEqual(_handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.INTERNAL_SERVER_ERROR,
                         'HTTP Status code not 500')

    def test_handler_retrieve_resource_missing_event(self):
        from fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                            'testing')
        _request_handler = RequestHandler(_dynamodb)

        _handler_retrieve_response = _request_handler.handler(None, None)

        self.assertEqual(_handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource(self):
        from fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_GET,
            Constants.EVENT_PATH_PARAMETERS: {Constants.EVENT_PATH_PARAMETER_IDENTIFIER: 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource_wrong_http_method(self):
        from fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.EVENT_HTTP_METHOD: 'POST',
            Constants.EVENT_PATH_PARAMETERS: {Constants.EVENT_PATH_PARAMETER_IDENTIFIER: 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource_not_found(self):
        from fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_GET,
            Constants.EVENT_PATH_PARAMETERS: {Constants.EVENT_PATH_PARAMETER_IDENTIFIER: 'fbf20333-35a5-4a06-9c58-68ea688a9a8b'}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.NOT_FOUND,
                         'HTTP Status code not 404')
        remove_mock_database(_dynamodb)

    @mock.patch.dict(os.environ, {'REGION': 'eu-west-1'})
    @mock.patch.dict(os.environ, {'TABLE_NAME': 'testing'})
    def test_handler_retrieve_resource_missing_resource_identifier(self):
        from fetch_resource.main.RequestHandler import RequestHandler
        _dynamodb = self.setup_mock_database('eu-west-1',
                                             'testing')
        _request_handler = RequestHandler(_dynamodb)

        _event = {
            Constants.EVENT_HTTP_METHOD: HttpConstants.HTTP_METHOD_GET,
            Constants.EVENT_PATH_PARAMETERS: {}
        }

        _handler_retrieve_response = _request_handler.handler(_event, None)

        self.assertEqual(_handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(_dynamodb)


if __name__ == '__main__':
    unittest.main()
