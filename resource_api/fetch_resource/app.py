import http
import os

from resource_api.common.constants import Constants
from resource_api.common.dynamo import DynamoDB
from resource_api.common.helpers import response

from resource_api.fetch_resource.main.RequestHandler import RequestHandler


_dynamodb = None


def handler(event, context):
    """
    Handler method for insert resource function.
    """

    global _dynamodb
    if _dynamodb is None:
        try:
            ddb = DynamoDB()
            _dynamodb = ddb.connect(os.environ[Constants.env_var_region()])
        except Exception as e:
            return response(http.HTTPStatus.INTERNAL_SERVER_ERROR, str(e))

    try:
        request_handler = RequestHandler(_dynamodb)
    except Exception as e:
        return response(http.HTTPStatus.INTERNAL_SERVER_ERROR, str(e))
    return request_handler.handler(event, context)
