class FileMetadata:
    def __init__(self, filename: str = None, mime_type: str = None, checksum: str = None, size: str = None):
        self.filename = filename
        self.mime_type = mime_type
        self.checksum = checksum
        self.size = size
