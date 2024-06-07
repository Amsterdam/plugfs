from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from typing import Collection, final


class FilesystemItem:
    def get_path(self) -> str: ...
    def get_name(self) -> str: ...


class DirectoryListing(Collection[FilesystemItem]):
    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[FilesystemItem]:
        pass

    def __contains__(self, __x: object) -> bool:
        pass


class Directory(FilesystemItem): ...


class File(FilesystemItem):
    def get_size(self) -> int: ...

    # TODO: read, write, metadata, etc


class Adapter(metaclass=ABCMeta):
    @abstractmethod
    async def list(self, path: str) -> DirectoryListing: ...


@final
class Filesystem:
    _adapter: Adapter

    def __init__(self, adapter: Adapter):
        self._adapter = adapter

    async def list(self, path: str) -> DirectoryListing:
        return await self._adapter.list(path)
