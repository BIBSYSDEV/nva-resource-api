"""Constants for use in NVA"""


class Constants:
    """Root class for constants for use in NVA"""

    ENV_VAR_REGION = 'REGION'
    ENV_VAR_TABLE_NAME = 'TABLE_NAME'

    EVENT_BODY = 'body'
    EVENT_HTTP_METHOD = 'httpMethod'
    EVENT_PATH_PARAMETERS = 'pathParameters'
    EVENT_PATH_PARAMETER_IDENTIFIER = 'identifier'
    EVENT_IDENTIFIER = 'identifier'

    RESPONSE_STATUS_CODE = 'statusCode'
    RESPONSE_BODY = 'body'
    RESPONSE_HEADERS = 'headers'

    DDB = 'dynamodb'
    DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS = 'Items'
    DDB_RESPONSE_ATTRIBUTE_NAME_RESPONSE_METADATA = 'ResponseMetadata'
    DDB_RESPONSE_ATTRIBUTE_NAME_RESPONSE_HTTP_STATUS_CODE = 'HTTPStatusCode'

    DDB_FIELD_IDENTIFIER = 'identifier'
    DDB_FIELD_MODIFIED_DATE = 'modifiedDate'
    DDB_FIELD_CREATED_DATE = 'createdDate'
    DDB_FIELD_FILE_SET = 'fileSet'
    DDB_FIELD_OWNER = 'owner'
    DDB_FIELD_ENTITY_DESCRIPTION = 'entityDescription'

    ERROR_MISSING_EVENT = 'Missing event'
    ERROR_INSUFFICIENT_PARAMETERS = 'Insufficient parameters'

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
    def ddb_response_attribute_name_response_metadata():
        """Returns the ResponseMetadata key for Dynamo DB response"""
        return 'ResponseMetadata'

    @staticmethod
    def ddb_response_attribute_name_response_http_status_code():
        """Returns the HTTPStatusCode key for Dynamo DB response"""
        return 'HTTPStatusCode'

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
    def ddb_field_file_set():
        """Returns the NVA field name for file set"""
        return 'fileSet'

    @staticmethod
    def ddb_field_owner():
        """Returns the NVA field name for owner"""
        return 'owner'

    @staticmethod
    def error_missing_event():
        """Returns the NVA error text for missing event"""
        return 'Missing event'

    @staticmethod
    def error_insufficient_parameters():
        """Returns the NVA error text for insufficient parameters"""
        return 'Insufficient parameters'
