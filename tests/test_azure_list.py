import os
from typing import AsyncGenerator, AsyncIterator

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import ContainerClient

from plugfs.azure import AzureFile, AzureStorageBlobsAdapter
from plugfs.filesystem import Directory


@pytest.fixture
async def container_client() -> AsyncGenerator[ContainerClient, None]:
    # Connect to the test container using environment-provided credentials.
    client = ContainerClient.from_connection_string(
        f"DefaultEndpointsProtocol=http;AccountName={os.getenv("AZURE_ACCOUNT_NAME")};"
        f"AccountKey={os.getenv("AZURE_ACCOUNT_KEY")};"
        f"BlobEndpoint={os.getenv("AZURE_STORAGE_URL")}/{os.getenv("AZURE_ACCOUNT_NAME")};",
        os.getenv("AZURE_CONTAINER", "default_container_name"),
    )

    async with client:
        # Ensure a clean state by deleting any previously existing container.
        try:
            await client.delete_container()
        except ResourceNotFoundError:
            pass

        await client.create_container()

        # Set up a two-level directory structure with two blobs for use across all tests.
        blob_client = client.get_blob_client("directory/subdirectory/1mb.bin")
        with open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "resources", "1mb.bin"
            ),
            "rb",
        ) as file:
            await blob_client.upload_blob(file)

        blob_client = client.get_blob_client("directory/subdirectory/10mb.bin")
        with open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "resources", "10mb.bin"
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


class TestAzureStorageBlobsAdapterList:
    @pytest.mark.anyio
    async def test_list_returns_single_deduplicated_top_level_directory(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        # Both blobs share the same top-level directory. Listing the root should
        # return it exactly once, not once per blob.
        items = await azure_storage_blobs_adapter.list("")

        assert len(items) == 1
        assert isinstance(items[0], Directory)
        assert items[0].path == "directory"

    @pytest.mark.anyio
    async def test_list_returns_subdirectory_when_no_direct_files_present(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        # "directory" contains no blobs directly, only a subdirectory. Listing
        # it should show that subdirectory only once and nothing else.
        items = await azure_storage_blobs_adapter.list("directory")

        assert len(items) == 1
        assert isinstance(items[0], Directory)
        assert items[0].path == "directory/subdirectory"

    @pytest.mark.anyio
    async def test_list_returns_all_files_in_leaf_directory(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        # "directory/subdirectory" is a directory, it contains blobs directly with no
        # further nesting. Both blobs should be returned as AzureFile instances.
        items = await azure_storage_blobs_adapter.list("directory/subdirectory")

        assert len(items) == 2
        assert isinstance(items[0], AzureFile)
        assert items[0].path == "directory/subdirectory/10mb.bin"
        assert isinstance(items[1], AzureFile)
        assert items[1].path == "directory/subdirectory/1mb.bin"
