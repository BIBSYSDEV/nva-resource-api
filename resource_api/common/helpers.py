"""Helper methods"""

from .constants import Constants
from .http_constants import HttpConstants
from os import environ


def remove_none_values(temp_value):
    """Remove None from dicts to ensure that nulls are ignored"""
    return_value = dict()
    for key, value in temp_value.items():
        if value is not None:
            return_value[key] = value
    return return_value


def response(status_code, body):
    """Formulates a response with status code and body"""
    headers = dict()
    if environ.get(Constants.env_var_allowed_origin()) is not None:
        headers[HttpConstants.http_header_access_control_allow_origin()] = environ.get(
            Constants.env_var_allowed_origin())

    return {
        Constants.response_status_code(): status_code,
        Constants.response_body(): body,
        Constants.response_headers(): headers
    }
