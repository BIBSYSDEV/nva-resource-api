"""Validation methods for AWS Dynamo DB resources in NVA"""


def validate_resource_insert(resource):
    """Validates resources for insertion into NVA"""
    if resource.resource_identifier is not None:
        raise ValueError('Resource has identifier')
    if resource.metadata is None:
        raise ValueError('Resource has no metadata')
    if resource.files is None:
        raise ValueError('Resource has no files')
    if resource.owner is None:
        raise ValueError('Resource has no owner')
    if not isinstance(resource.metadata, dict):
        raise ValueError('Resource has invalid attribute type for metadata')
    if not isinstance(resource.files, dict):
        raise ValueError('Resource has invalid attribute type for files')


def validate_resource_modify(resource):
    """Validates resources for updating in NVA"""
    if resource.resource_identifier is None:
        raise ValueError('Resource has no identifier')
    if resource.metadata is None:
        raise ValueError('Resource with identifier '
                         + resource.resource_identifier + ' has no metadata')
    if resource.files is None:
        raise ValueError('Resource with identifier '
                         + resource.resource_identifier + ' has no files')
    if resource.owner is None:
        raise ValueError('Resource with identifier '
                         + resource.resource_identifier + ' has no owner')
    if not isinstance(resource.metadata, dict):
        raise ValueError(
            'Resource with identifier '
            + resource.resource_identifier + ' has invalid attribute type for metadata')
    if not isinstance(resource.files, dict):
        raise ValueError(
            'Resource with identifier '
            + resource.resource_identifier + ' has invalid attribute type for files')
