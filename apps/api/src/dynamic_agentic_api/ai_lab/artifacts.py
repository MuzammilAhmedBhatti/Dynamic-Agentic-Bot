from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Protocol


class ExperimentArtifactStore(Protocol):
    async def put_json(
        self, organization_id: uuid.UUID, experiment_id: uuid.UUID, name: str, value: object
    ) -> str: ...


class LocalExperimentArtifactStore:
    """Development-only artifact adapter; production can replace it with Cloud Storage."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    async def put_json(
        self, organization_id: uuid.UUID, experiment_id: uuid.UUID, name: str, value: object
    ) -> str:
        safe_name = "".join(
            character for character in name if character.isalnum() or character in "-_"
        )
        path = self._root / str(organization_id) / str(experiment_id) / f"{safe_name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, separators=(",", ":")), encoding="utf-8")
        return str(path.relative_to(self._root))
