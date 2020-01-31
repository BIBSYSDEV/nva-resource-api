from .metadata import Metadata


class Resource:

    def __init__(self, resource_identifier: str = None, modified_date: str = None, created_date: str = None,
                 metadata: Metadata = None, files: dict = None, owner: str = None, status: str = None,
                 indexed_date: str = None, published_date: str = None):
        self.resource_identifier = resource_identifier
        self.modified_date = modified_date
        self.created_date = created_date
        self.metadata = metadata
        self.files = files
        self.owner = owner
        self.indexed_date = indexed_date
        self.published_date = published_date
        self.status = status

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
