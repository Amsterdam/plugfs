from aiofiles.os import listdir
from aiofiles.ospath import isdir

from plugfs.filesystem import Adapter, Directory, DirectoryListing, File, FilesystemItem


class LocalAdapter(Adapter):
    async def list(self, path: str) -> DirectoryListing:
        contents = await listdir(path)
        items: list[FilesystemItem] = []
        for item in contents:
            filepath = f"{path}/{item}"
            if await isdir(filepath):
                items.append(Directory(filepath, item))
            else:
                items.append(File(filepath, item))

        return items
