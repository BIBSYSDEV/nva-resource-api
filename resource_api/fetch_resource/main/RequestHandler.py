import http
import json
import os

from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table
from resource_api.common.http_constants import HttpConstants
from resource_api.common.constants import Constants

from resource_api.common.helpers import response


class RequestHandler:

    def __init__(self, dynamodb=None):

        self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.env_var_table_name())
        self.table: Table = self.dynamodb.Table(self.table_name)

    def __retrieve_resource(self, uuid):
        _ddb_response = self.table.query(
            KeyConditionExpression=Key(Constants.ddb_field_identifier()).eq(uuid),
            ScanIndexForward=False
        )
        return _ddb_response

    def handler(self, event, context):
        """
        Request handler method for fetch resource function.
        """
        if event is None or Constants.event_path_parameters() not in event:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())

        if Constants.event_path_parameter_identifier() not in event[Constants.event_path_parameters()]:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())

        _identifier = event[Constants.event_path_parameters()][Constants.event_path_parameter_identifier()]
        _http_method = event[Constants.event_http_method()]

        if _http_method == HttpConstants.http_method_get() and _identifier:
            _ddb_response = self.__retrieve_resource(_identifier)
            if len(_ddb_response[Constants.ddb_response_attribute_name_items()]) == 0:
                return response(http.HTTPStatus.NOT_FOUND, json.dumps(_ddb_response))
            return response(http.HTTPStatus.OK, json.dumps(_ddb_response))
        return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())
