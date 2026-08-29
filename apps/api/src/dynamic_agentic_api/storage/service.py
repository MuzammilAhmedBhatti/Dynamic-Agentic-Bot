from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Protocol

from google.cloud import storage


class StorageService(Protocol):
    async def put(self, object_key: str, data: bytes) -> str: ...

    async def read(self, object_ref: str) -> bytes: ...

    async def delete(self, object_ref: str) -> None: ...


class LocalStorageService:
    """Development adapter; callers receive opaque references, never filesystem paths."""

    _key_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,999}$")

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    async def put(self, object_key: str, data: bytes) -> str:
        path = self._resolve_key(object_key)
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, data)
        return f"local://{object_key}"

    async def read(self, object_ref: str) -> bytes:
        return await asyncio.to_thread(self._resolve_ref(object_ref).read_bytes)

    async def delete(self, object_ref: str) -> None:
        path = self._resolve_ref(object_ref)
        if path.exists():
            await asyncio.to_thread(path.unlink)

    def _resolve_ref(self, object_ref: str) -> Path:
        if not object_ref.startswith("local://"):
            raise ValueError("unsupported object reference")
        return self._resolve_key(object_ref.removeprefix("local://"))

    def _resolve_key(self, object_key: str) -> Path:
        if not self._key_pattern.fullmatch(object_key) or ".." in object_key.split("/"):
            raise ValueError("invalid object key")
        path = (self._root / object_key).resolve()
        if not path.is_relative_to(self._root):
            raise ValueError("object key escapes storage root")
        return path


class GcsStorageService:
    """Private Cloud Storage adapter returning opaque, application-authorized references."""

    _key_pattern = LocalStorageService._key_pattern

    def __init__(self, bucket_name: str) -> None:
        self._bucket_name = bucket_name
        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket_name)

    async def put(self, object_key: str, data: bytes) -> str:
        key = self._validate_key(object_key)
        await asyncio.to_thread(self._bucket.blob(key).upload_from_string, data)
        return f"gcs://{self._bucket_name}/{key}"

    async def read(self, object_ref: str) -> bytes:
        key = self._resolve_ref(object_ref)
        return await asyncio.to_thread(self._bucket.blob(key).download_as_bytes)

    async def delete(self, object_ref: str) -> None:
        key = self._resolve_ref(object_ref)
        await asyncio.to_thread(self._bucket.blob(key).delete)

    def _resolve_ref(self, object_ref: str) -> str:
        prefix = f"gcs://{self._bucket_name}/"
        if not object_ref.startswith(prefix):
            raise ValueError("unsupported object reference")
        return self._validate_key(object_ref.removeprefix(prefix))

    def _validate_key(self, object_key: str) -> str:
        if not self._key_pattern.fullmatch(object_key) or ".." in object_key.split("/"):
            raise ValueError("invalid object key")
        return object_key
