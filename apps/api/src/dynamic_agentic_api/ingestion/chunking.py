from __future__ import annotations

import re

from dynamic_agentic_api.ingestion.contracts import ExtractedPage, TextChunk


class RecursivePageChunker:
    version = "recursive-page-v1"
    _paragraph_break = re.compile(r"\n\s*\n")

    def __init__(self, *, chunk_size: int, overlap: int) -> None:
        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("invalid chunk configuration")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: list[ExtractedPage]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        ordinal = 0
        for page in pages:
            for text in self._split(page.text):
                if not text.strip():
                    continue
                chunks.append(
                    TextChunk(
                        ordinal=ordinal,
                        page_number=page.page_number,
                        text=text.strip(),
                        title=page.title,
                        section=page.section,
                        chunker_version=self.version,
                        chunk_size=self.chunk_size,
                        overlap=self.overlap,
                    )
                )
                ordinal += 1
        return chunks

    def _split(self, text: str) -> list[str]:
        normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if len(normalized) <= self.chunk_size:
            return [normalized] if normalized else []
        paragraphs = [
            part.strip() for part in self._paragraph_break.split(normalized) if part.strip()
        ]
        units: list[str] = []
        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                units.append(paragraph)
            else:
                units.extend(self._hard_split(paragraph))
        chunks: list[str] = []
        current = ""
        for unit in units:
            candidate = f"{current}\n\n{unit}".strip() if current else unit
            if current and len(candidate) > self.chunk_size:
                chunks.append(current)
                prefix = current[-self.overlap :] if self.overlap else ""
                combined = f"{prefix}\n\n{unit}".strip()
                # A hard-split unit may already consume the full budget. In
                # that case it carries its own overlap and must stand alone.
                current = combined if len(combined) <= self.chunk_size else unit
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks

    def _hard_split(self, text: str) -> list[str]:
        step = self.chunk_size - self.overlap
        return [text[start : start + self.chunk_size] for start in range(0, len(text), step)]
