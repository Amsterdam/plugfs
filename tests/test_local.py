from os import path

import pytest

from plugfs.filesystem import Directory, File, NotFoundException
from plugfs.local import LocalAdapter


class TestLocalAdapter:
    @pytest.mark.asyncio
    async def test_list(self) -> None:
        adapter = LocalAdapter()
        items = await adapter.list(path.join(path.dirname(__file__), "resources"))

        assert len(items) == 2

        assert isinstance(items[0], File)
        assert items[0].path == path.join(
            path.abspath(path.dirname(__file__)), "resources", "1mb.bin"
        )
        assert await items[0].size == 1048576

        assert isinstance(items[1], Directory)
        assert items[1].path == path.join(
            path.abspath(path.dirname(__file__)), "resources", "directory"
        )

    @pytest.mark.asyncio
    async def test_list_non_existing(self) -> None:
        adapter = LocalAdapter()
        with pytest.raises(NotFoundException) as exception_info:
            await adapter.list("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to retrieve directory listing for '/this/path/does/not/exist'!"
        )

    @pytest.mark.asyncio
    async def test_read(self) -> None:
        adapter = LocalAdapter()

        data = await adapter.read(
            path.join(path.abspath(path.dirname(__file__)), "resources", "1mb.bin")
        )

        assert len(data) == 1048576

    @pytest.mark.asyncio
    async def test_read_non_existing(self) -> None:
        adapter = LocalAdapter()

        with pytest.raises(NotFoundException) as exception_info:
            await adapter.read("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to find file '/this/path/does/not/exist'!"
        )