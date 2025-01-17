class DupFilesRemoverBaseError(Exception):
    pass


class FolderDoesNotExistsError(DupFilesRemoverBaseError):
    pass


class FileMaskIsNotSupportedError(DupFilesRemoverBaseError):
    def __init__(self, mask, *args, **kwargs):
        self.mask = mask
        super().__init__(*args, **kwargs)
