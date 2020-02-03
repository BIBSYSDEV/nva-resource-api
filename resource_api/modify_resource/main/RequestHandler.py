import http
import json
import os
from json import JSONDecodeError

from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table
from resource_api.common.constants import Constants
from resource_api.common.http_constants import HttpConstants
from resource_api.common.helpers import response


class RequestHandler:

    def __init__(self, dynamodb=None):

        self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.ENV_VAR_TABLE_NAME)
        self.table: Table = self.dynamodb.Table(self.table_name)

    def get_table_connection(self):
        return self.table

    def modify_resource(self, modified_resource):
        ddb_response = self.table.query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_RESOURCE_IDENTIFIER).eq(
                modified_resource[Constants.EVENT_RESOURCE_IDENTIFIER]))

        if len(ddb_response[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS]) == 0:
            raise ValueError('Resource with identifier ' + modified_resource[Constants.EVENT_RESOURCE_IDENTIFIER] + ' not found')

        ddb_response = self.table.put_item(Item=modified_resource)
        return ddb_response

    def handler(self, event, context):
        if event is None or Constants.EVENT_PATH_PARAMETERS not in event:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)

        if Constants.EVENT_PATH_PARAMETER_IDENTIFIER not in event[Constants.EVENT_PATH_PARAMETERS]:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)

        try:
            body = json.loads(event[Constants.EVENT_BODY])
        except JSONDecodeError as e:
            return response(http.HTTPStatus.BAD_REQUEST, e.args[0])

        identifier = event[Constants.EVENT_PATH_PARAMETERS][Constants.EVENT_PATH_PARAMETER_IDENTIFIER]
        http_method = event[Constants.EVENT_HTTP_METHOD]

        if http_method == HttpConstants.HTTP_METHOD_PUT and body is not None:
            try:
                ddb_response = self.modify_resource(body)
                ddb_response[Constants.EVENT_RESOURCE_IDENTIFIER] = identifier
                return response(http.HTTPStatus.OK, json.dumps(ddb_response))
            except ValueError as e:
                return response(http.HTTPStatus.BAD_REQUEST, e.args[0])

        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
