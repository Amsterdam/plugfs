from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from typing import final


class _FilesystemItem:
    _path: str

    def __init__(self, path: str):
        self._path = path

    @property
    def path(self) -> str:
        return self._path


DirectoryListing = Sequence[_FilesystemItem]


class Directory(_FilesystemItem): ...


class File(_FilesystemItem, metaclass=ABCMeta):
    @property
    @abstractmethod
    async def size(self) -> int: ...

    @abstractmethod
    async def read(self) -> bytes: ...


class NotFoundException(Exception): ...


class Adapter(metaclass=ABCMeta):
    @abstractmethod
    async def list(self, path: str) -> DirectoryListing: ...

    @abstractmethod
    async def read(self, path: str) -> bytes: ...

    @abstractmethod
    async def get_file(self, path: str) -> File: ...

    @abstractmethod
    async def write(self, path: str, data: bytes) -> File: ...

    @abstractmethod
    async def makedirs(self, path: str) -> None: ...


@final
class Filesystem:
    _adapter: Adapter

    def __init__(self, adapter: Adapter):
        self._adapter = adapter

    async def list(self, path: str) -> DirectoryListing:
        return await self._adapter.list(path)

    async def get_file(self, path: str) -> File:
        return await self._adapter.get_file(path)

    async def write(self, path: str, data: bytes) -> File:
        return await self._adapter.write(path, data)

    async def makedirs(self, path: str) -> None:
        return await self._adapter.makedirs(path)
