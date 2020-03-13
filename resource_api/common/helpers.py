"""Helper methods"""

from .constants import Constants
from .http_constants import HttpConstants
from os import environ


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
