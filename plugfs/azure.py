import os

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import ContainerClient

from plugfs.filesystem import (
    Adapter,
    Directory,
    DirectoryListing,
    File,
    NotFoundException,
    _FilesystemItem,
)


class AzureFile(File):
    _adapter: "AzureStorageBlobsAdapter"

    def __init__(self, path: str, adapter: "AzureStorageBlobsAdapter"):
        super().__init__(path)
        self._adapter = adapter

    @property
    async def size(self) -> int:
        return await self._adapter.get_size(self._path)

    async def read(self) -> bytes:
        return await self._adapter.read(self._path)


class AzureStorageBlobsAdapter(Adapter):
    _client: ContainerClient

    def __init__(self, client: ContainerClient):
        self._client = client

    async def list(self, path: str) -> DirectoryListing:
        if not path == "" and not path.endswith("/"):
            path += "/"

        items: list[_FilesystemItem] = []

        async for blob in self._client.list_blobs(name_starts_with=path):
            relative_path = os.path.relpath(blob.name, path)

            if not "/" in relative_path:
                items.append(AzureFile(blob.name, self))
            else:
                directory_name = os.path.dirname(relative_path)
                if directory_name and not "/" in directory_name:
                    items.append(Directory(f"{path}{directory_name}"))

        return items

    async def read(self, path: str) -> bytes:
        blob_client = self._client.get_blob_client(path)
        try:
            stream = await blob_client.download_blob()
        except ResourceNotFoundError as error:
            raise NotFoundException(f"Failed to find file '{path}'!") from error

        return await stream.readall()

    async def get_file(self, path: str) -> File:
        raise NotImplementedError()

    async def write(self, path: str, data: bytes) -> File:
        raise NotImplementedError()

    async def get_size(self, path: str) -> int:
        blob_client = self._client.get_blob_client(path)
        try:
            stream = await blob_client.download_blob()
        except ResourceNotFoundError as error:
            raise NotFoundException(f"Failed to find file '{path}'!") from error

        return stream.size
