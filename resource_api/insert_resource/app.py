import http
import os

from resource_api.common.constants import Constants
from resource_api.common.dynamo import DynamoDB
from resource_api.common.helpers import response

from resource_api.insert_resource.main.RequestHandler import RequestHandler


_dynamodb = None


def handler(event, context):
    """
    Handler method for insert resource function.
    """
    if event is None:
        return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())
    if event is None or Constants.event_body() not in event or Constants.event_http_method() not in event:
        return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())
    if event[Constants.event_body()] is None or len(event[Constants.event_body()]) is 0:
        return response(http.HTTPStatus.BAD_REQUEST, Constants.error_insufficient_parameters())

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


def clear_dynamodb():
    """
    Clear the global dynamodb instance.
    """
    globals()['_dynamodb'] = None
    