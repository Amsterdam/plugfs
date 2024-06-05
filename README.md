# Filesystem abstraction

```mermaid
classDiagram
    class Fileystem
    class Adapter
    <<interface>> Adapter
    class File
    class Directory

    Fileystem *-- Adapter
    Directory *-- File
    Fileystem *-- Directory
```