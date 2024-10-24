import os
from typing import AsyncGenerator, AsyncIterator

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import ContainerClient

from plugfs.azure import AzureFile, AzureStorageBlobsAdapter
from plugfs.filesystem import Directory, NotFoundException


@pytest.fixture
async def container_client() -> AsyncGenerator[ContainerClient, None]:
    client = ContainerClient.from_connection_string(
        f"DefaultEndpointsProtocol=http;AccountName={os.getenv("AZURE_ACCOUNT_NAME")};"
        f"AccountKey={os.getenv("AZURE_ACCOUNT_KEY")};"
        f"BlobEndpoint={os.getenv("AZURE_STORAGE_URL")}/{os.getenv("AZURE_ACCOUNT_NAME")};",
        os.getenv("AZURE_CONTAINER", "default_container_name"),
    )

    async with client:
        try:
            await client.delete_container()
        except ResourceNotFoundError:
            """No need to delete the container if it does not exist."""

        await client.create_container()

        blob_client = client.get_blob_client("/1mb.bin")
        with open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "resources", "1mb.bin"
            ),
            "rb",
        ) as file:
            await blob_client.upload_blob(file)

        blob_client = client.get_blob_client("/10mb.bin")
        with open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "resources", "10mb.bin"
            ),
            "rb",
        ) as file:
            await blob_client.upload_blob(file)

        blob_client = client.get_blob_client("/directory/256kb.bin")
        with open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "resources",
                "directory",
                "256kb.bin",
            ),
            "rb",
        ) as file:
            await blob_client.upload_blob(file)

        blob_client = client.get_blob_client("/directory/subdirectory/nested_file")
        with open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "resources",
                "directory",
                "256kb.bin",
            ),
            "rb",
        ) as file:
            await blob_client.upload_blob(file)

        yield client


@pytest.fixture
def azure_storage_blobs_adapter(
    container_client: ContainerClient,
) -> AzureStorageBlobsAdapter:
    return AzureStorageBlobsAdapter(container_client)


class TestAzureStorageBlobsAdapter:
    @pytest.mark.anyio
    async def test_list_root(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        items = await azure_storage_blobs_adapter.list("/")

        assert len(items) == 3

        assert isinstance(items[0], AzureFile)
        assert items[0].path == "/10mb.bin"
        assert await items[0].size == 10485760

        assert isinstance(items[1], AzureFile)
        assert items[1].path == "/1mb.bin"
        assert await items[1].size == 1048576

        assert isinstance(items[2], Directory)
        assert items[2].path == "/directory"

    @pytest.mark.anyio
    async def test_list_directory(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        items = await azure_storage_blobs_adapter.list("/directory")

        assert len(items) == 2

        assert isinstance(items[0], AzureFile)
        assert items[0].path == "/directory/256kb.bin"

        assert isinstance(items[1], Directory)
        assert items[1].path == "/directory/subdirectory"

    @pytest.mark.anyio
    async def test_list_subdirectory(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        items = await azure_storage_blobs_adapter.list("/directory/subdirectory")

        assert len(items) == 1

        assert isinstance(items[0], AzureFile)
        assert items[0].path == "/directory/subdirectory/nested_file"

    @pytest.mark.anyio
    async def test_list_non_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        items = await azure_storage_blobs_adapter.list("/this/path/does/not/exist")
        assert len(items) == 0

    @pytest.mark.anyio
    async def test_read(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        data = await azure_storage_blobs_adapter.read("/1mb.bin")

        assert len(data) == 1048576

    @pytest.mark.anyio
    async def test_read_non_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        with pytest.raises(NotFoundException) as exception_info:
            await azure_storage_blobs_adapter.read("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to find file '/this/path/does/not/exist'!"
        )

    @pytest.mark.anyio
    async def test_get_iterator(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        iterator = await azure_storage_blobs_adapter.get_iterator("/10mb.bin")

        data = None
        count = 0
        async for chunk in iterator:
            count += 1
            if data is None:
                data = chunk
                continue

            data += chunk

        assert data is not None
        assert len(data) == 10485760
        assert count == 3

    @pytest.mark.anyio
    async def test_get_iterator_non_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        with pytest.raises(NotFoundException) as exception_info:
            await azure_storage_blobs_adapter.get_iterator("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to find file '/this/path/does/not/exist'!"
        )

    @pytest.mark.anyio
    async def test_get_file(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file = await azure_storage_blobs_adapter.get_file("/1mb.bin")

        assert isinstance(file, AzureFile)

    @pytest.mark.anyio
    async def test_get_file_non_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        with pytest.raises(NotFoundException) as exception_info:
            await azure_storage_blobs_adapter.get_file("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to find file '/this/path/does/not/exist'!"
        )

    @pytest.mark.anyio
    async def test_write_new(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file = await azure_storage_blobs_adapter.write("/new_file", b"Hello world!")

        assert await file.size == 12

    @pytest.mark.anyio
    async def test_write_overwrite_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file = await azure_storage_blobs_adapter.write("/1mb.bin", b"Hello world!")

        assert await file.size == 12

    @pytest.mark.anyio
    async def test_write_iterator_new(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file = await azure_storage_blobs_adapter.write_iterator(
            "/new_iterator_file", self._iterator()
        )

        assert await file.size == 12

    @pytest.mark.anyio
    async def test_write_overwrite_iterator_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file = await azure_storage_blobs_adapter.write_iterator(
            "/1mb.bin", self._iterator()
        )

        assert await file.size == 12

    async def _iterator(self) -> AsyncIterator[bytes]:
        for chunk in [b"Hello ", b"world", b"!"]:
            yield chunk

    @pytest.mark.anyio
    async def test_delete_non_existing(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file_path = "/this/path/does/not/exist"

        with pytest.raises(NotFoundException) as exception_info:
            await azure_storage_blobs_adapter.delete(file_path)

        assert (
            str(exception_info.value)
            == f"Failed to delete file '{file_path}', file does not exist!"
        )

    @pytest.mark.anyio
    async def test_delete(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        file_path = "/1mb.bin"
        await azure_storage_blobs_adapter.delete(file_path)

        with pytest.raises(NotFoundException) as exception_info:
            await azure_storage_blobs_adapter.get_file(file_path)

        assert str(exception_info.value) == f"Failed to find file '{file_path}'!"
