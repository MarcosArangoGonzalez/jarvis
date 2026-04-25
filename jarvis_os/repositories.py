from __future__ import annotations

import json
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel, TypeAdapter

from .schemas import Event, IngestionResult, Job, NewsletterResult, ResearchResult, SecurityFinding


T = TypeVar("T", bound=BaseModel)


class JsonListRepository(Generic[T]):
    def __init__(self, path: Path, model: type[T]) -> None:
        self.path = path
        self.model = model
        self.adapter = TypeAdapter(list[model])
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[T]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        return self.adapter.validate_python(payload)

    def save(self, items: list[T]) -> None:
        content = self.adapter.dump_python(items, mode="json")
        self.path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


class JobRepository(JsonListRepository[Job]):
    def __init__(self, path: Path) -> None:
        super().__init__(path, Job)

    def add(self, job: Job) -> Job:
        items = self.load()
        items.insert(0, job)
        self.save(items[:100])
        return job

    def update(self, job: Job) -> Job:
        items = self.load()
        updated = [job if existing.id == job.id else existing for existing in items]
        if not any(existing.id == job.id for existing in items):
            updated.insert(0, job)
        self.save(updated[:100])
        return job


class EventRepository(JsonListRepository[Event]):
    def __init__(self, path: Path) -> None:
        super().__init__(path, Event)

    def add(self, event: Event) -> Event:
        items = self.load()
        items.insert(0, event)
        self.save(items[:300])
        return event


class IngestionRepository(JsonListRepository[IngestionResult]):
    def __init__(self, path: Path) -> None:
        super().__init__(path, IngestionResult)

    def add(self, result: IngestionResult) -> IngestionResult:
        items = self.load()
        items.insert(0, result)
        self.save(items[:200])
        return result


class ResearchRepository(JsonListRepository[ResearchResult]):
    def __init__(self, path: Path) -> None:
        super().__init__(path, ResearchResult)

    def add(self, result: ResearchResult) -> ResearchResult:
        items = self.load()
        items.insert(0, result)
        self.save(items[:100])
        return result


class NewsletterRepository(JsonListRepository[NewsletterResult]):
    def __init__(self, path: Path) -> None:
        super().__init__(path, NewsletterResult)

    def add(self, result: NewsletterResult) -> NewsletterResult:
        items = [item for item in self.load() if item.date != result.date]
        items.insert(0, result)
        self.save(items[:100])
        return result


class SecurityFindingRepository(JsonListRepository[SecurityFinding]):
    def __init__(self, path: Path) -> None:
        super().__init__(path, SecurityFinding)

    def replace(self, findings: list[SecurityFinding]) -> list[SecurityFinding]:
        self.save(findings[:500])
        return findings[:500]
