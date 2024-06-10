from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from typing import final


class FilesystemItem:
    _path: str
    _name: str

    def __init__(self, path: str, name: str):
        self._path = path
        self._name = name

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._name


DirectoryListing = Sequence[FilesystemItem]


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
