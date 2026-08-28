from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import func, select

from dynamic_agentic_api.db.models import AgentTraceEvent
from dynamic_agentic_api.db.session import async_session_factory


@dataclass(frozen=True, slots=True)
class SafeTraceEvent:
    sequence: int
    run_id: uuid.UUID
    event_type: str
    stage: str
    occurred_at: str
    duration_ms: int | None
    safe_summary: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["run_id"] = str(self.run_id)
        return payload


class TraceHub:
    def __init__(self) -> None:
        self._subscribers: dict[uuid.UUID, set[asyncio.Queue[SafeTraceEvent]]] = {}
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def subscribe(self, run_id: uuid.UUID) -> AsyncIterator[asyncio.Queue[SafeTraceEvent]]:
        queue: asyncio.Queue[SafeTraceEvent] = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers.setdefault(run_id, set()).add(queue)
        try:
            yield queue
        finally:
            async with self._lock:
                subscribers = self._subscribers.get(run_id)
                if subscribers:
                    subscribers.discard(queue)
                    if not subscribers:
                        self._subscribers.pop(run_id, None)

    async def publish(self, event: SafeTraceEvent) -> None:
        async with self._lock:
            queues = list(self._subscribers.get(event.run_id, set()))
        for queue in queues:
            if not queue.full():
                queue.put_nowait(event)


class TraceService:
    _allowed_summary_keys: ClassVar[frozenset[str]] = frozenset(
        {
            "route",
            "candidate_count",
            "citation_count",
            "support",
            "provider",
            "model",
            "error_code",
            "persona",
            "selection_mode",
            "route_count",
            "source_type",
            "row_count",
            "table_count",
            "operation",
            "suggestion_count",
        }
    )

    def __init__(self, hub: TraceHub) -> None:
        self.hub = hub

    async def emit(
        self,
        *,
        run_id: uuid.UUID,
        event_type: str,
        stage: str,
        duration_ms: int | None = None,
        safe_summary: dict[str, object] | None = None,
    ) -> SafeTraceEvent:
        sanitized: dict[str, object] = {
            key: value
            for key, value in (safe_summary or {}).items()
            if key in self._allowed_summary_keys and isinstance(value, (str, int, float, bool))
        }
        occurred_at = datetime.now(UTC)
        async with async_session_factory() as session:
            last_sequence = await session.scalar(
                select(func.coalesce(func.max(AgentTraceEvent.sequence), 0)).where(
                    AgentTraceEvent.run_id == run_id
                )
            )
            sequence = int(last_sequence or 0) + 1
            session.add(
                AgentTraceEvent(
                    run_id=run_id,
                    sequence=sequence,
                    event_type=event_type,
                    stage=stage,
                    duration_ms=duration_ms,
                    safe_summary=sanitized,
                    occurred_at=occurred_at,
                )
            )
            await session.commit()
        event = SafeTraceEvent(
            sequence=sequence,
            run_id=run_id,
            event_type=event_type,
            stage=stage,
            occurred_at=occurred_at.isoformat(),
            duration_ms=duration_ms,
            safe_summary=sanitized,
        )
        await self.hub.publish(event)
        return event
