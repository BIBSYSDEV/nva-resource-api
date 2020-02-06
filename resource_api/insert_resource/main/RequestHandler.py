import http
import simplejson as json
from simplejson import JSONDecodeError
import os

from boto3_type_annotations.dynamodb import Table
from resource_api.common.http_constants import HttpConstants
from resource_api.common.constants import Constants
from resource_api.common.helpers import response


class RequestHandler:

    def __init__(self, dynamodb=None):

        self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.env_var_table_name())
        self.table: Table = self.dynamodb.Table(self.table_name)

    def get_table_connection(self):
        return self.table

    def insert_resource(self, resource):
        ddb_response = self.table.put_item(
            Item=resource
        )
        return ddb_response

    def handler(self, event, context):
        """
        Request handler method for insert resource function.
        """

        if event is None:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())

        try:
            body = event[Constants.event_body()]
            print(body)
            body_as_json = json.loads(body)
        except JSONDecodeError as e:
            return response(http.HTTPStatus.BAD_REQUEST, str(e))

        http_method = event[Constants.event_http_method()]

        if http_method == HttpConstants.http_method_post() and body_as_json is not None:
            ddb_response = self.insert_resource(body_as_json)
            return response(http.HTTPStatus.CREATED, json.dumps(ddb_response))

        return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())
