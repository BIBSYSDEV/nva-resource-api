"""Constants for HTTP"""


class HttpConstants:
    """Root class for http constants for use in NVA"""

    @staticmethod
    def http_method_get():
        """Returns the HTTP method name GET"""
        return 'GET'

    @staticmethod
    def http_method_post():
        """Returns the HTTP method name POST"""
        return 'POST'

    @staticmethod
    def http_method_put():
        """Returns the HTTP method name PUT"""
        return 'PUT'

    @staticmethod
    def http_header_access_control_allow_origin():
        """Returns the string for CORS header Access-Control-Allow-Origin"""
        return 'Access-Control-Allow-Origin'
