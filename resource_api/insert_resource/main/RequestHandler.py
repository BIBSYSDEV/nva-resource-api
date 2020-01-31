import http
import json
import os
import uuid
from json import JSONDecodeError

import arrow as arrow
from boto3_type_annotations.dynamodb import Table
from resource_api.common.http_constants import HttpConstants
from resource_api.common.constants import Constants
from resource_api.common.helpers import response
from resource_api.common.validator import validate_resource_insert
from resource_api.data.resource import Resource


class RequestHandler:

    def __init__(self, dynamodb=None):

        self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.ENV_VAR_TABLE_NAME)
        self.table: Table = self.dynamodb.Table(self.table_name)

    def get_table_connection(self):
        return self.table

    def insert_resource(self, generated_uuid, current_time, resource):
        ddb_response = self.table.put_item(
            Item={
                Constants.DDB_FIELD_RESOURCE_IDENTIFIER: generated_uuid,
                Constants.DDB_FIELD_MODIFIED_DATE: current_time,
                Constants.DDB_FIELD_CREATED_DATE: current_time,
                Constants.DDB_FIELD_METADATA: resource.metadata,
                Constants.DDB_FIELD_FILES: resource.files,
                Constants.DDB_FIELD_OWNER: resource.owner
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

        if http_method == HttpConstants.HTTP_METHOD_POST and resource is not None:
            try:
                validate_resource_insert(resource)
            except ValueError as e:
                return response(http.HTTPStatus.BAD_REQUEST, e.args[0])
            generated_uuid = uuid.uuid4().__str__()
            ddb_response = self.insert_resource(generated_uuid, current_time, resource)
            ddb_response['resource_identifier'] = generated_uuid
            return response(http.HTTPStatus.CREATED, json.dumps(ddb_response))

        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
