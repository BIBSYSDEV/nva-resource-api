import http
import json
import os
from json import JSONDecodeError

import arrow as arrow
from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table
from resource_api.common.constants import Constants
from resource_api.common.http_constants import HttpConstants
from resource_api.common.helpers import response
from resource_api.common.validator import validate_resource_modify
from resource_api.data.resource import Resource


class RequestHandler:

    def __init__(self, dynamodb=None):

        self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.ENV_VAR_TABLE_NAME)
        self.table: Table = self.dynamodb.Table(self.table_name)

    def get_table_connection(self):
        return self.table

    def modify_resource(self, current_time, modified_resource):
        ddb_response = self.table.query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_RESOURCE_IDENTIFIER).eq(
                modified_resource.resource_identifier))

        if len(ddb_response[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS]) == 0:
            raise ValueError('Resource with identifier ' + modified_resource.resource_identifier + ' not found')

        previous_resource = ddb_response[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][0]
        if Constants.DDB_FIELD_CREATED_DATE not in previous_resource:
            raise ValueError(
                'Resource with identifier ' + modified_resource.resource_identifier + ' has no ' +
                Constants.DDB_FIELD_CREATED_DATE + ' in DB')

        ddb_response = self.table.put_item(
            Item={
                Constants.DDB_FIELD_RESOURCE_IDENTIFIER: modified_resource.resource_identifier,
                Constants.DDB_FIELD_MODIFIED_DATE: current_time,
                Constants.DDB_FIELD_CREATED_DATE: previous_resource[Constants.DDB_FIELD_CREATED_DATE],
                Constants.DDB_FIELD_METADATA: modified_resource.metadata,
                Constants.DDB_FIELD_FILES: modified_resource.files,
                Constants.DDB_FIELD_OWNER: modified_resource.owner
            }
        )
        return ddb_response

    def handler(self, event, context):

        try:
            body = json.loads(event[Constants.EVENT_BODY])
        except JSONDecodeError as e:
            return response(http.HTTPStatus.BAD_REQUEST, e.args[0])

        http_method = event[Constants.EVENT_HTTP_METHOD]
        resource_dict_from_json = body.get(Constants.JSON_ATTRIBUTE_NAME_RESOURCE)

        try:
            resource = Resource.from_dict(resource_dict_from_json)
        except TypeError as e:
            return response(http.HTTPStatus.BAD_REQUEST, e.args[0])

        current_time = arrow.utcnow().isoformat()

        resource_not_none = resource is not None
        if http_method == HttpConstants.HTTP_METHOD_PUT and resource_not_none:
            try:
                validate_resource_modify(resource)
                ddb_response = self.modify_resource(current_time, resource)
                ddb_response['resource_identifier'] = resource.resource_identifier
                return response(http.HTTPStatus.OK, json.dumps(ddb_response))
            except ValueError as e:
                return response(http.HTTPStatus.BAD_REQUEST, e.args[0])

        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
