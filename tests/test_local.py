from os import path

import pytest

from plugfs.filesystem import Directory, File, Filesystem
from plugfs.local import LocalAdapter


@pytest.mark.asyncio
async def test_list() -> None:
    filesystem = Filesystem(LocalAdapter())
    items = await filesystem.list(path.join(path.dirname(__file__), "resources"))

    assert len(items) == 2

    assert isinstance(items[0], File)
    assert items[0].name == "1mb.bin"
    assert items[0].path == path.join(
        path.abspath(path.dirname(__file__)), "resources", "1mb.bin"
    )
    assert items[0].size == 1048576

    assert isinstance(items[1], Directory)
    assert items[1].name == "directory"
    assert items[1].path == path.join(
        path.abspath(path.dirname(__file__)), "resources", "directory"
    )
