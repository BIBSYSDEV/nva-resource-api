"""Helper methods"""

from .constants import Constants


def remove_none_values(temp_value):
    """Remove None from dicts to ensure that nulls are ignored"""
    return_value = dict()
    for key, value in temp_value.items():
        if value is not None:
            return_value[key] = value
    return return_value


def response(status_code, body):
    """Formulates a response with status code and body"""
    return {
        Constants.RESPONSE_STATUS_CODE: status_code,
        Constants.RESPONSE_BODY: body
    }
