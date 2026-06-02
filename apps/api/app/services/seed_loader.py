from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eval_case import EvalCase
from app.models.knowledge_document import KnowledgeDocument


@dataclass(frozen=True)
class SeedLoadSummary:
    knowledge_documents_created: int = 0
    knowledge_documents_updated: int = 0
    eval_cases_created: int = 0
    eval_cases_updated: int = 0

    @property
    def knowledge_documents_loaded(self) -> int:
        return self.knowledge_documents_created + self.knowledge_documents_updated

    @property
    def eval_cases_loaded(self) -> int:
        return self.eval_cases_created + self.eval_cases_updated


@dataclass(frozen=True)
class SeedDocument:
    source_path: str
    title: str
    document_type: str
    content: str
    metadata: dict[str, Any]


def find_seed_root(start: Path | None = None) -> Path:
    search_start = start or Path(__file__).resolve()
    for parent in [search_start, *search_start.parents]:
        seed_root = parent / "seed"
        if seed_root.is_dir():
            return seed_root
    raise FileNotFoundError("Could not locate repo-level seed directory")


def detect_document_type(path: Path) -> str:
    parts = set(path.parts)
    if "mock_logs" in parts:
        return "mock_log"
    if "schemas" in parts:
        return "schema"
    if "runbooks" in parts:
        return "runbook"
    return "document"


def discover_seed_documents(seed_root: Path) -> list[SeedDocument]:
    paths = [
        *sorted((seed_root / "documents").glob("**/*.md")),
        *sorted((seed_root / "mock_logs").glob("**/*.log")),
    ]
    documents: list[SeedDocument] = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        documents.append(
            SeedDocument(
                source_path=path.relative_to(seed_root.parent).as_posix(),
                title=_title_for_path(path, content),
                document_type=detect_document_type(path),
                content=content,
                metadata={"file_name": path.name},
            )
        )
    return documents


def load_eval_cases(seed_root: Path) -> list[dict[str, Any]]:
    eval_path = seed_root / "eval_cases" / "incident-triage-evals.json"
    if not eval_path.exists():
        return []
    loaded = json.loads(eval_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError("Eval seed file must contain a JSON array")
    return loaded


def load_seed_data(db: Session, seed_root: Path | None = None) -> SeedLoadSummary:
    root = seed_root or find_seed_root()
    docs_created = docs_updated = evals_created = evals_updated = 0

    for document in discover_seed_documents(root):
        existing = db.scalar(
            select(KnowledgeDocument).where(KnowledgeDocument.source_path == document.source_path)
        )
        if existing is None:
            db.add(
                KnowledgeDocument(
                    source_path=document.source_path,
                    title=document.title,
                    document_type=document.document_type,
                    content=document.content,
                    metadata_=document.metadata,
                )
            )
            docs_created += 1
        else:
            existing.title = document.title
            existing.document_type = document.document_type
            existing.content = document.content
            existing.metadata_ = document.metadata
            docs_updated += 1

    for eval_case in load_eval_cases(root):
        name = _require_string(eval_case, "name")
        existing = db.scalar(select(EvalCase).where(EvalCase.name == name))
        expected_signals = {
            "source_id": eval_case.get("id"),
            "category": eval_case.get("category"),
            "difficulty": eval_case.get("difficulty"),
            "risk_level": eval_case.get("risk_level"),
            "expected_capability": eval_case.get("expected_capability"),
            "workflow_tags": eval_case.get("workflow_tags", []),
            "mock_evidence": eval_case.get("mock_evidence", []),
            "expected_diagnosis": eval_case.get("expected_diagnosis"),
            "expected_evidence": eval_case.get("expected_evidence", []),
            "safe_next_steps": eval_case.get("safe_next_steps", []),
            "expected_keywords": eval_case.get("expected_keywords", []),
            "expected_failure_modes": eval_case.get("expected_failure_modes", []),
            "minimum_score": eval_case.get("minimum_score"),
        }
        tags = eval_case.get("tags", eval_case.get("workflow_tags", ["incident-triage"]))

        if existing is None:
            db.add(
                EvalCase(
                    name=name,
                    task=_require_string(eval_case, "task"),
                    expected_signals=expected_signals,
                    tags=tags,
                    is_active=True,
                )
            )
            evals_created += 1
        else:
            existing.task = _require_string(eval_case, "task")
            existing.expected_signals = expected_signals
            existing.tags = tags
            existing.is_active = True
            evals_updated += 1

    db.commit()
    return SeedLoadSummary(
        knowledge_documents_created=docs_created,
        knowledge_documents_updated=docs_updated,
        eval_cases_created=evals_created,
        eval_cases_updated=evals_updated,
    )


def _title_for_path(path: Path, content: str) -> str:
    if path.suffix == ".md":
        first_line = content.splitlines()[0] if content.splitlines() else ""
        if first_line.startswith("# "):
            return first_line.removeprefix("# ").strip()
    return path.stem.replace("-", " ").title()


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Eval case is missing required string field: {key}")
    return value
