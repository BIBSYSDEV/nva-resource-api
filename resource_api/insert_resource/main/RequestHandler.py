import http
import json
import os
from json import JSONDecodeError

from boto3_type_annotations.dynamodb import Table
from common.http_constants import HttpConstants
from common.constants import Constants
from common.helpers import response


class RequestHandler:

    def __init__(self, dynamodb=None):

        self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.ENV_VAR_TABLE_NAME)
        self.table: Table = self.dynamodb.Table(self.table_name)

    def get_table_connection(self):
        return self.table

    def insert_resource(self, resource):
        ddb_response = self.table.put_item(
            Item=resource
        )
        return ddb_response

    def handler(self, event, context):

        try:
            body = json.loads(event[Constants.EVENT_BODY])
        except JSONDecodeError as e:
            return response(http.HTTPStatus.BAD_REQUEST, e.args[0])

        http_method = event[Constants.EVENT_HTTP_METHOD]

        if http_method == HttpConstants.HTTP_METHOD_POST and body is not None:
            ddb_response = self.insert_resource(body)
            return response(http.HTTPStatus.CREATED, json.dumps(ddb_response))

        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
