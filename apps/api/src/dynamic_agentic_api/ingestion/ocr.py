from __future__ import annotations

from typing import Protocol


class OcrService(Protocol):
    async def extract_page_text(self, page_png: bytes) -> str | None: ...


class UnavailableOcrService:
    async def extract_page_text(self, page_png: bytes) -> str | None:
        del page_png
        return None
