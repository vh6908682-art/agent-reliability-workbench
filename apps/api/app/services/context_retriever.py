from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.services.seed_loader import SeedDocument, discover_seed_documents, find_seed_root


DEFAULT_KEYWORDS = {
    "kafka",
    "consumer",
    "duplicate",
    "key",
    "violation",
    "retry",
    "retries",
    "exhaustion",
    "customer",
    "update",
    "event",
    "idempotency",
    "replay",
    "schema",
}

PRIORITY_TERMS = {
    "kafka": 3,
    "consumer": 3,
    "duplicate": 4,
    "key": 2,
    "violation": 4,
    "retry": 3,
    "retries": 3,
    "exhaustion": 3,
    "customer": 2,
    "update": 2,
    "event": 2,
    "idempotency": 4,
    "replay": 3,
}


@dataclass(frozen=True)
class RetrievedContext:
    source_path: str
    title: str
    document_type: str
    content: str
    relevance_score: int


class SeedContextRetriever:
    def __init__(self, seed_root: Path | None = None, max_results: int = 4) -> None:
        self.seed_root = seed_root
        self.max_results = max_results

    def retrieve(self, task: str) -> list[RetrievedContext]:
        seed_root = self.seed_root or find_seed_root()
        task_terms = _tokens(task) | DEFAULT_KEYWORDS
        scored_documents = [
            self._score_document(document, task_terms)
            for document in discover_seed_documents(seed_root)
        ]

        matches = [context for context in scored_documents if context.relevance_score > 0]
        matches.sort(key=lambda context: (-context.relevance_score, context.source_path))
        return matches[: self.max_results]

    def _score_document(self, document: SeedDocument, task_terms: set[str]) -> RetrievedContext:
        searchable = f"{document.title}\n{document.document_type}\n{document.content}".lower()
        score = 0
        for term in task_terms:
            if term in searchable:
                score += PRIORITY_TERMS.get(term, 1)

        return RetrievedContext(
            source_path=document.source_path,
            title=document.title,
            document_type=document.document_type,
            content=document.content,
            relevance_score=score,
        )


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))
