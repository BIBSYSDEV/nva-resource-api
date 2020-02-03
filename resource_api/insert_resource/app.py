import http
import os

from common.constants import Constants
from common.dynamo import DynamoDB
from common.helpers import response

from insert_resource.main.RequestHandler import RequestHandler


_dynamodb = None


def handler(event, context):
    if event is None:
        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
    if event is None or Constants.EVENT_BODY not in event or Constants.EVENT_HTTP_METHOD not in event:
        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
    if event[Constants.EVENT_BODY] is None or len(event[Constants.EVENT_BODY]) is 0:
        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)

    global _dynamodb
    if _dynamodb is None:
        try:
            ddb = DynamoDB()
            _dynamodb = ddb.connect(os.environ[Constants.ENV_VAR_REGION])
        except Exception as e:
            return response(http.HTTPStatus.INTERNAL_SERVER_ERROR, e.args[0])

    try:
        request_handler = RequestHandler(_dynamodb)
    except Exception as e:
        return response(http.HTTPStatus.INTERNAL_SERVER_ERROR, e.args[0])
    return request_handler.handler(event, context)


def clear_dynamodb():
    globals()['_dynamodb'] = None