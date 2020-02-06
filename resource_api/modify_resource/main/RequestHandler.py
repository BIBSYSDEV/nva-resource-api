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

        self.table_name = os.environ.get(Constants.env_var_table_name())
        self.table: Table = self.dynamodb.Table(self.table_name)

    def modify_resource(self, modified_resource):
        ddb_response = self.table.query(
            KeyConditionExpression=Key(Constants.ddb_field_identifier()).eq(
                modified_resource[Constants.event_identifier()]))

        if len(ddb_response[Constants.ddb_response_attribute_name_items()]) == 0:
            raise ValueError('Resource with identifier ' + modified_resource[Constants.event_identifier()] + ' not found')

        ddb_response = self.table.put_item(Item=modified_resource)
        return ddb_response

    def handler(self, event, context):
        """
        Request handler method for modify resource function.
        """
        if event is None or Constants.event_path_parameters() not in event:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())

        if Constants.event_path_parameter_identifier() not in event[Constants.event_path_parameters()]:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())

        try:
            body = json.loads(event[Constants.event_body()])
        except JSONDecodeError as e:
            return response(http.HTTPStatus.BAD_REQUEST, str(e))

        identifier = event[Constants.event_path_parameters()][Constants.event_path_parameter_identifier()]
        http_method = event[Constants.event_http_method()]

        if http_method == HttpConstants.http_method_put() and body is not None:
            try:
                ddb_response = self.modify_resource(body)
                ddb_response[Constants.event_identifier()] = identifier
                return response(http.HTTPStatus.OK, json.dumps(ddb_response))
            except ValueError as e:
                return response(http.HTTPStatus.BAD_REQUEST, str(e))

        return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())
