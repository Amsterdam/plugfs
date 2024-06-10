import aiofiles
from aiofiles.os import listdir
from aiofiles.ospath import getsize, isdir

from plugfs.filesystem import Adapter, Directory, DirectoryListing, File, FilesystemItem


class LocalFile(File):
    _adapter: "LocalAdapter"
    _size: int

    def __init__(
        self, path: str, name: str, size: int, adapter: "LocalAdapter"
    ) -> None:
        super().__init__(path, name)
        self._size = size
        self._adapter = adapter

    @property
    def size(self) -> int:
        return self._size

    async def read(self) -> bytes:
        return await self._adapter.read(self._path)


class LocalAdapter(Adapter):
    async def list(self, path: str) -> DirectoryListing:
        contents = await listdir(path)
        items: list[FilesystemItem] = []
        for item in contents:
            filepath = f"{path}/{item}"
            if await isdir(filepath):
                items.append(Directory(filepath, item))
            else:
                items.append(LocalFile(filepath, item, await getsize(filepath), self))

        return items

    async def read(self, path: str) -> bytes:
        async with aiofiles.open(path, mode="rb") as file:
            data = await file.read()

        return data
