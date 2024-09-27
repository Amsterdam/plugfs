import os
from os import path
from uuid import uuid4

import pytest

from plugfs.filesystem import Directory, NotFoundException
from plugfs.local import LocalAdapter, LocalFile


class TestLocalAdapter:
    @pytest.mark.anyio
    async def test_list(self) -> None:
        adapter = LocalAdapter()
        items = await adapter.list(path.join(path.dirname(__file__), "resources"))

        assert len(items) == 2

        file_found = False
        directory_found = False
        for item in items:
            if isinstance(item, LocalFile):
                assert item.path == path.join(
                    path.abspath(path.dirname(__file__)), "resources", "1mb.bin"
                )
                assert await item.size == 1048576
                file_found = True
            elif isinstance(item, Directory):
                assert item.path == path.join(
                    path.abspath(path.dirname(__file__)), "resources", "directory"
                )
                directory_found = True
        assert file_found is True and directory_found is True

    @pytest.mark.anyio
    async def test_list_non_existing(self) -> None:
        adapter = LocalAdapter()
        with pytest.raises(NotFoundException) as exception_info:
            await adapter.list("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to retrieve directory listing for '/this/path/does/not/exist'!"
        )

    @pytest.mark.anyio
    async def test_read(self) -> None:
        adapter = LocalAdapter()

        data = await adapter.read(
            path.join(path.abspath(path.dirname(__file__)), "resources", "1mb.bin")
        )

        assert len(data) == 1048576

    @pytest.mark.anyio
    async def test_read_non_existing(self) -> None:
        adapter = LocalAdapter()

        with pytest.raises(NotFoundException) as exception_info:
            await adapter.read("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to find file '/this/path/does/not/exist'!"
        )

    @pytest.mark.anyio
    async def test_get_file(self) -> None:
        adapter = LocalAdapter()

        file = await adapter.get_file(
            path.join(path.abspath(path.dirname(__file__)), "resources", "1mb.bin")
        )

        assert isinstance(file, LocalFile)

    @pytest.mark.anyio
    async def test_get_file_non_existing(self) -> None:
        adapter = LocalAdapter()

        with pytest.raises(NotFoundException) as exception_info:
            await adapter.get_file("/this/path/does/not/exist")

        assert (
            str(exception_info.value)
            == "Failed to find file '/this/path/does/not/exist'!"
        )

    @pytest.mark.anyio
    async def test_write_new(self) -> None:
        adapter = LocalAdapter()
        filepath = path.join("/tmp", str(uuid4()))

        file = await adapter.write(filepath, b"Hello world!")
        assert await file.size == 12

        os.remove(filepath)

    @pytest.mark.anyio
    async def test_write_overwrite_existing(self) -> None:
        adapter = LocalAdapter()
        filepath = path.join("/tmp", str(uuid4()))
        with open(filepath, "wb") as file:
            file.write(b"Hello!")

        local_file = await adapter.write(filepath, b"Hello world!")
        assert await local_file.size == 12

        os.remove(filepath)

    @pytest.mark.anyio
    async def test_write_non_existing_directory(self) -> None:
        adapter = LocalAdapter()

        with pytest.raises(NotFoundException) as exception_info:
            await adapter.write("/this/path/does/not/exist", b"Hello world!")

        assert (
            str(exception_info.value)
            == "Failed to write file '/this/path/does/not/exist', directory does not exist!"
        )

    @pytest.mark.anyio
    async def test_makedirs(self) -> None:
        adapter = LocalAdapter()
        dir_path = path.join("/tmp", str(uuid4()))

        await adapter.makedirs(dir_path)

        assert path.exists(dir_path)

        os.rmdir(dir_path)
