from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ScanResult:
    clean: bool
    reason_code: str | None = None


class MalwareScanner(Protocol):
    async def scan(self, data: bytes, filename: str) -> ScanResult: ...


class SignatureOnlyMalwareScanner:
    """Milestone hook: enforces the PDF signature; production AV plugs into this interface."""

    async def scan(self, data: bytes, filename: str) -> ScanResult:
        del filename
        if not data.startswith(b"%PDF-"):
            return ScanResult(clean=False, reason_code="INVALID_PDF_SIGNATURE")
        return ScanResult(clean=True)
