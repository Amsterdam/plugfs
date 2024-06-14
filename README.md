# Filesystem abstraction

```mermaid
classDiagram
    class Fileystem {
        -adapter Adapter
        +list(path str) DirectoryListing
        +get_file(path str) File
        +write(path str, data bytes) File
    }
    class Adapter {
        +list(path str) DirectoryListing*
        +read(path str) bytes*
        +get_file(path str) File*
        +write(path str, data bytes) File*
    }
    <<interface>> Adapter
    class _FilesystemItem {
        +path str
    }
    class File {
        +size: int*
        +read() bytes*
        +write(data bytes)*
    }
    <<abstract>> File
    class Directory
    class DirectoryListing
    class LocalAdapter {
        +list(path str) DirectoryListing
        +read(path str) bytes
        +get_file(path str) LocalFile
        +write(path str, data bytes) LocalFile
    }
    class LocalFile {
        -adapter LocalAdapter
        +size: int
        +read() bytes
        +write(data bytes)
    }
    class AzureStorageBlobsAdapter {
        -client ContainerClient
        +list(path str) DirectoryListing
        +read(path str) bytes
        +get_file(path str) AzureFile
        +write(path str, data bytes) AzureFile
        +get_size(path str) int
    }
    class AzureFile {
        -adapter AzureStorageBlobsAdapter
        +size: int
        +read() bytes
        +write(data bytes)
    }

    Fileystem *-- Adapter
    File --|> _FilesystemItem
    Directory --|> _FilesystemItem
    DirectoryListing *-- File
    DirectoryListing *-- Directory
    LocalAdapter --|> Adapter
    LocalFile --|> File
    AzureStorageBlobsAdapter --|> Adapter
    AzureFile --|> File
```

The idea behind this library is to provide an abstraction layer for your code. That way it doesn't matter what storage
backend is used.

We do this by setting up an adapter of choice and providing it to the `Filesystem` class.
In turn, we use the `Filesystem` object in our code to perform operations like reading and writing files.

If for whatever reason at some point we decide to use a different storage backend, all we would need to do is provide
the `Filesystem` with a different adapter.
