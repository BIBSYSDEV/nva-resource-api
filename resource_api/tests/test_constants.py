"""Constants for use in NVA testing"""

class TestConstants:
    """Root class for constants for use in NVA testing"""

    @staticmethod
    def env_var_aws_access_key_id():
        """Returns the key name for aws access key id environment variable"""
        return 'AWS_ACCESS_KEY_ID'

    @staticmethod
    def env_var_aws_session_token():
        """Returns the key name for aws session token environment variable"""
        return 'AWS_SESSION_TOKEN'

    @staticmethod
    def env_var_aws_security_token():
        """Returns the key name for aws security token environment variable"""
        return 'AWS_SECURITY_TOKEN'

    @staticmethod
    def env_var_aws_secret_access_key():
        """Returns the key name for aws secret access key environment variable"""
        return 'AWS_SECRET_ACCESS_KEY'