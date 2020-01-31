"""Utility to help encoding between dicts and JSON"""

from resource_api.common.helpers import remove_none_values

from resource_api.data.file_metadata import FileMetadata
from resource_api.data.creator import Creator
from resource_api.data.metadata import Metadata
from resource_api.data.resource import Resource


def encode_file_metadata(instance):
    """Utility method to encode FileMetadata objects"""

    if not isinstance(instance, FileMetadata):
        type_name = instance.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

    temp_value = {
        'filename': instance.filename,
        'mimetype': instance.mime_type,
        'checksum': instance.checksum,
        'size': instance.size
    }
    return remove_none_values(temp_value)


def encode_files(instance):
    """Utility method to encode dictionaries of FileMetadata objects"""
    if instance is None:
        return None

    if not isinstance(instance, dict):
        type_name = instance.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

    files = dict()
    for key, value in instance.items():
        files[key] = encode_file_metadata(value)
    return files


def encode_creator(instance):
    """Utility method to encode Creator objects"""
    if not isinstance(instance, Creator):
        type_name = instance.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

    return instance.identifier


def encode_metadata(instance):
    """Utility method to encode Metadata objects"""
    if instance is None:
        return None
    if not isinstance(instance, Metadata):
        type_name = instance.__class__.__name__
        raise TypeError(f"Object of type {type_name} is not JSON serializable")

    if instance.creators is None:
        creators = None
    else:
        creators = []
        for creator in instance.creators:
            creators.append(encode_creator(creator))

    if instance.titles is None:
        titles = None
    else:
        titles = dict()
        for key, value in instance.titles.items():
            if value is not None:
                titles[key] = value
        if len(titles.keys()) == 0:
            titles = None
    temp_value = {
        'creators': creators,
        'handle': instance.handle,
        'license': instance.license_identifier,
        'publicationYear': instance.publication_year,
        'publisher': instance.publisher,
        'titles': titles,
        'type': instance.resource_type
    }
    return remove_none_values(temp_value)


def encode_resource(instance):
    """Utility method to encode Resource objects"""
    if instance is None:
        return None
    if not isinstance(instance, Resource):
        type_name = instance.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

    temp_value = {
        'resource_identifier': instance.resource_identifier,
        'modifiedDate': instance.modified_date,
        'createdDate': instance.created_date,
        'metadata': encode_metadata(instance.metadata),
        'files': encode_files(instance.files),
        'owner': instance.owner,
        'status': instance.status,
        'publishedDate': instance.published_date,
        'indexedDate': instance.indexed_date
    }
    return remove_none_values(temp_value)
