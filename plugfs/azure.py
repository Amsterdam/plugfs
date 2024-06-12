from azure.storage.blob.aio import ContainerClient

from plugfs.filesystem import Adapter, DirectoryListing, File


class AzureStorageBlobsAdapter(Adapter):
    _client: ContainerClient

    def __init__(self, client: ContainerClient):
        self._client = client

    async def list(self, path: str) -> DirectoryListing:
        raise NotImplementedError()

    async def read(self, path: str) -> bytes:
        raise NotImplementedError()

    async def get_file(self, path: str) -> File:
        raise NotImplementedError()

    async def write(self, path: str, data: bytes) -> File:
        raise NotImplementedError()
