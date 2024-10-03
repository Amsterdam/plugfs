from typing import AsyncIterator, final

import aiofiles
from aiofiles.os import listdir, makedirs
from aiofiles.ospath import exists, getsize, isdir, isfile

from plugfs.filesystem import (
    Adapter,
    Directory,
    DirectoryListing,
    File,
    NotFoundException,
    _FilesystemItem,
)


@final
class LocalFile(File):
    _adapter: "LocalAdapter"

    def __init__(self, path: str, adapter: "LocalAdapter") -> None:
        super().__init__(path)
        self._adapter = adapter

    @property
    async def size(self) -> int:
        return await getsize(self._path)

    async def read(self) -> bytes:
        return await self._adapter.read(self._path)

    async def get_iterator(self) -> AsyncIterator[bytes]:
        return await self._adapter.get_iterator(self._path)

    async def write(self, data: bytes) -> None:
        await self._adapter.write(self._path, data)


@final
class LocalAdapter(Adapter):
    async def list(self, path: str) -> DirectoryListing:
        try:
            contents = await listdir(path)
        except FileNotFoundError as error:
            raise NotFoundException(
                f"Failed to retrieve directory listing for '{path}'!"
            ) from error

        items: list[_FilesystemItem] = []
        for item in contents:
            filepath = f"{path}/{item}"
            if await isdir(filepath):
                items.append(Directory(filepath))
            else:
                items.append(LocalFile(filepath, self))

        return items

    async def read(self, path: str) -> bytes:
        try:
            async with aiofiles.open(path, mode="rb") as file:
                data = await file.read()
        except FileNotFoundError as error:
            raise NotFoundException(f"Failed to find file '{path}'!") from error

        return data

    async def get_iterator(self, path: str) -> AsyncIterator[bytes]:
        if not await exists(path) or not await isfile(path):
            raise NotFoundException(f"Failed to find file '{path}'!")

        async def iterate() -> AsyncIterator[bytes]:
            async with aiofiles.open(path, mode="rb") as file:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    yield chunk

        return iterate()

    async def get_file(self, path: str) -> LocalFile:
        if await exists(path) and await isfile(path):
            return LocalFile(path, self)

        raise NotFoundException(f"Failed to find file '{path}'!")

    async def write(self, path: str, data: bytes) -> LocalFile:
        try:
            async with aiofiles.open(path, mode="wb") as file:
                await file.write(data)
        except FileNotFoundError as error:
            raise NotFoundException(
                f"Failed to write file '{path}', directory does not exist!"
            ) from error

        return LocalFile(path, self)

    async def makedirs(self, path: str) -> None:
        await makedirs(path)
