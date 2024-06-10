from aiofiles.os import listdir
from aiofiles.ospath import getsize, isdir

from plugfs.filesystem import Adapter, Directory, DirectoryListing, File, FilesystemItem


class LocalFile(File):
    _size: int

    def __init__(self, path: str, name: str, size: int):
        super().__init__(path, name)
        self._size = size

    @property
    def size(self) -> int:
        return self._size


class LocalAdapter(Adapter):
    async def list(self, path: str) -> DirectoryListing:
        contents = await listdir(path)
        items: list[FilesystemItem] = []
        for item in contents:
            filepath = f"{path}/{item}"
            if await isdir(filepath):
                items.append(Directory(filepath, item))
            else:
                items.append(LocalFile(filepath, item, await getsize(filepath)))

        return items
