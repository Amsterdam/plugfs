import os

import pytest
import pytest_asyncio
from azure.storage.blob.aio import ContainerClient

from plugfs.azure import AzureStorageBlobsAdapter


@pytest_asyncio.fixture
async def container_client() -> ContainerClient:
    client = ContainerClient.from_connection_string(
        f"DefaultEndpointsProtocol=http;AccountName={os.getenv("AZURE_ACCOUNT_NAME")};"
        f"AccountKey={os.getenv("AZURE_ACCOUNT_KEY")};"
        f"BlobEndpoint={os.getenv("AZURE_STORAGE_URL")}/{os.getenv("AZURE_ACCOUNT_NAME")};",
        os.getenv("AZURE_CONTAINER", "default_container_name"),
    )

    await client.create_container()

    blob_client = client.get_blob_client("1mb.bin")

    with open(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "resources", "1mb.bin"
        ),
        "rb",
    ) as file:
        await blob_client.upload_blob(file)

    return client


@pytest.fixture
def azure_storage_blobs_adapter(
    container_client: ContainerClient,
) -> AzureStorageBlobsAdapter:
    return AzureStorageBlobsAdapter(container_client)


class TestAzureStorageBlobsAdapter:
    @pytest.mark.asyncio
    async def test_list(
        self, azure_storage_blobs_adapter: AzureStorageBlobsAdapter
    ) -> None:
        items = await azure_storage_blobs_adapter.list("/")
