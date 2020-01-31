from .file_metadata import FileMetadata


class File:
    def __init__(self, identifier: str = None, file_metadata: FileMetadata = None):
        self.identifier = identifier
        self.file_metadata = file_metadata
