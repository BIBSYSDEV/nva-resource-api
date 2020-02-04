import http
import os

from resource_api.common.constants import Constants
from resource_api.common.dynamo import DynamoDB
from resource_api.common.helpers import response

from resource_api.fetch_resource.main.RequestHandler import RequestHandler


_dynamodb = None


def handler(event, context):

    global _dynamodb
    if _dynamodb is None:
        try:
            ddb = DynamoDB()
            _dynamodb = ddb.connect(os.environ[Constants.env_var_region()])
            _dynamodb
        except Exception as e:
            return response(http.HTTPStatus.INTERNAL_SERVER_ERROR, e.args[0])

    try:
        request_handler = RequestHandler(_dynamodb)
    except Exception as e:
        return response(http.HTTPStatus.INTERNAL_SERVER_ERROR, e.args[0])
    return request_handler.handler(event, context)
