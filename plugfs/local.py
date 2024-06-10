import aiofiles
from aiofiles.os import listdir
from aiofiles.ospath import getsize, isdir

from plugfs.filesystem import Adapter, Directory, DirectoryListing, File, FilesystemItem


class LocalFile(File):
    _adapter: "LocalAdapter"

    def __init__(self, path: str, name: str, adapter: "LocalAdapter") -> None:
        super().__init__(path, name)
        self._adapter = adapter

    @property
    async def size(self) -> int:
        return await getsize(self._path)

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
                items.append(LocalFile(filepath, item, self))

        return items

    async def read(self, path: str) -> bytes:
        async with aiofiles.open(path, mode="rb") as file:
            data = await file.read()

        return data
