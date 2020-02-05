"""Constants for use in NVA"""


class Constants:
    """Root class for constants for use in NVA"""

    @staticmethod
    def env_var_region():
        """Returns the key name for region environment variable"""
        return 'REGION'

    @staticmethod
    def env_var_table_name():
        """Returns the key name for table name environment variable"""
        return 'TABLE_NAME'

    @staticmethod
    def event_body():
        """Returns the key for the body element of an event"""
        return 'body'

    @staticmethod
    def event_http_method():
        """Returns the key for the http method element of an event"""
        return 'httpMethod'

    @staticmethod
    def event_path_parameters():
        """Returns the key for the path parameters element of an event"""
        return 'pathParameters'

    @staticmethod
    def event_path_parameter_identifier():
        """Returns the key for the identifier element of an event"""
        return 'identifier'

    @staticmethod
    def event_identifier():
        """Returns the key for the identifier element of an event"""
        return 'identifier'

    @staticmethod
    def response_status_code():
        """Returns the status code key for Response objects"""
        return 'statusCode'

    @staticmethod
    def response_body():
        """Returns the body key for Response objects"""
        return 'body'

    @staticmethod
    def response_headers():
        """Returns the headers key for Response objects"""
        return 'headers'

    @staticmethod
    def ddb():
        """Returns AWS service name for Dynamo DB"""
        return 'dynamodb'

    @staticmethod
    def ddb_response_attribute_name_items():
        """Returns the Items key for a Dynamo DB response"""
        return 'Items'

    @staticmethod
    def ddb_response_attribute_name_count():
        """Returns the Count key for a Dynamo DB response"""
        return 'Count'

    @staticmethod
    def ddb_field_identifier():
        """Returns the NVA field name for identifier"""
        return 'identifier'

    @staticmethod
    def ddb_field_modified_date():
        """Returns the NVA field name for modified date"""
        return 'modifiedDate'

    @staticmethod
    def ddb_field_created_date():
        """Returns the NVA field name for created date"""
        return 'createdDate'

    @staticmethod
    def ddb_field_entity_description():
        """Returns the NVA field name for entity description"""
        return 'entityDescription'

    @staticmethod
    def error_insufficient_parameters():
        """Returns the NVA error text for insufficient parameters"""
        return 'Insufficient parameters'

    @staticmethod
    def env_var_allowed_origin():
        """Returns the key name for allowed origin environment variable"""
        return 'ALLOWED_ORIGIN'
