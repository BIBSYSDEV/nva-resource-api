from typing import List

from .creator import Creator


class Metadata:
    def __init__(self, creators: List[Creator] = None, handle: str = None, license_identifier: str = None,
                 publication_year: str = None, publisher: str = None, titles: dict = None, resource_type: str = None):
        self.creators = creators
        self.handle = handle
        self.license_identifier = license_identifier
        self.publication_year = publication_year
        self.publisher = publisher
        self.titles = titles
        self.resource_type = resource_type
