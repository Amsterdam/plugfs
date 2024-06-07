import pytest

from plugfs.filesystem import Filesystem
from plugfs.local import LocalAdapter


@pytest.mark.asyncio
async def test_list() -> None:
    filesystem = Filesystem(LocalAdapter())
    items = await filesystem.list("/")
    for item in items:
        print(item)
