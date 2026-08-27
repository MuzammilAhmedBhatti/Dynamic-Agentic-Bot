from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    page_number: int
    text: str
    preview_png: bytes
    title: str | None = None
    section: str | None = None


@dataclass(frozen=True, slots=True)
class TextChunk:
    ordinal: int
    page_number: int
    text: str
    title: str | None
    section: str | None
    chunker_version: str
    chunk_size: int
    overlap: int
