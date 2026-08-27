from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pymupdf

from dynamic_agentic_api.ingestion.contracts import ExtractedPage


class PdfValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PdfInspection:
    page_count: int


class PdfProcessor:
    renderer_version = f"pymupdf-{pymupdf.VersionBind}"

    async def inspect(self, data: bytes, max_pages: int) -> PdfInspection:
        return await asyncio.to_thread(self._inspect_sync, data, max_pages)

    async def extract_and_render(self, data: bytes, max_pages: int) -> list[ExtractedPage]:
        return await asyncio.to_thread(self._extract_sync, data, max_pages)

    @staticmethod
    def _open(data: bytes) -> pymupdf.Document:
        if not data.startswith(b"%PDF-"):
            raise PdfValidationError("INVALID_PDF_SIGNATURE")
        try:
            document = pymupdf.open(stream=data, filetype="pdf")
        except (pymupdf.FileDataError, RuntimeError) as exc:
            raise PdfValidationError("INVALID_PDF") from exc
        if document.needs_pass:
            document.close()
            raise PdfValidationError("ENCRYPTED_PDF_UNSUPPORTED")
        return document

    @classmethod
    def _inspect_sync(cls, data: bytes, max_pages: int) -> PdfInspection:
        document = cls._open(data)
        try:
            page_count = document.page_count
            if page_count < 1:
                raise PdfValidationError("EMPTY_PDF")
            if page_count > max_pages:
                raise PdfValidationError("PDF_PAGE_LIMIT_EXCEEDED")
            return PdfInspection(page_count=page_count)
        finally:
            document.close()

    @classmethod
    def _extract_sync(cls, data: bytes, max_pages: int) -> list[ExtractedPage]:
        inspection = cls._inspect_sync(data, max_pages)
        document = cls._open(data)
        pages: list[ExtractedPage] = []
        try:
            for index in range(inspection.page_count):
                page = document.load_page(index)
                text = page.get_text("text", sort=True).strip()
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
                first_line = next(
                    (line.strip() for line in text.splitlines() if line.strip()), None
                )
                title = first_line[:300] if first_line and len(first_line) <= 300 else None
                pages.append(
                    ExtractedPage(
                        page_number=index + 1,
                        text=text,
                        preview_png=pixmap.tobytes("png"),
                        title=title,
                        section=title,
                    )
                )
        finally:
            document.close()
        return pages
