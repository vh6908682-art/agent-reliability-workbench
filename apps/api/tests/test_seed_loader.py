import json
from pathlib import Path
from typing import Any

from sqlalchemy.sql.elements import BinaryExpression

from app.models.eval_case import EvalCase
from app.models.knowledge_document import KnowledgeDocument
from app.services.seed_loader import (
    detect_document_type,
    discover_seed_documents,
    load_eval_cases,
    load_seed_data,
)


class FakeSession:
    def __init__(self) -> None:
        self.knowledge_documents: dict[str, KnowledgeDocument] = {}
        self.eval_cases: dict[str, EvalCase] = {}
        self.commits = 0

    def scalar(self, statement: Any) -> Any:
        where_clause = statement._where_criteria[0]
        key = _where_value(where_clause)
        table_name = statement.column_descriptions[0]["entity"].__tablename__
        if table_name == "knowledge_documents":
            return self.knowledge_documents.get(key)
        if table_name == "eval_cases":
            return self.eval_cases.get(key)
        raise AssertionError(f"Unexpected table: {table_name}")

    def add(self, instance: Any) -> None:
        if isinstance(instance, KnowledgeDocument):
            self.knowledge_documents[instance.source_path] = instance
            return
        if isinstance(instance, EvalCase):
            self.eval_cases[instance.name] = instance
            return
        raise AssertionError(f"Unexpected instance: {instance}")

    def commit(self) -> None:
        self.commits += 1


def test_document_type_detection() -> None:
    assert detect_document_type(Path("seed/documents/runbooks/kafka.md")) == "runbook"
    assert detect_document_type(Path("seed/documents/schemas/customer.md")) == "schema"
    assert detect_document_type(Path("seed/mock_logs/customer.log")) == "mock_log"
    assert detect_document_type(Path("seed/documents/other.md")) == "document"


def test_seed_file_discovery(tmp_path: Path) -> None:
    seed_root = tmp_path / "seed"
    runbook = seed_root / "documents" / "runbooks" / "retry.md"
    schema = seed_root / "documents" / "schemas" / "customer.md"
    log = seed_root / "mock_logs" / "consumer.log"
    runbook.parent.mkdir(parents=True)
    schema.parent.mkdir(parents=True)
    log.parent.mkdir(parents=True)
    runbook.write_text("# Retry Runbook\nBody", encoding="utf-8")
    schema.write_text("# Customer Schema\nBody", encoding="utf-8")
    log.write_text("ERROR duplicate key", encoding="utf-8")

    documents = discover_seed_documents(seed_root)

    assert [document.source_path for document in documents] == [
        "seed/documents/runbooks/retry.md",
        "seed/documents/schemas/customer.md",
        "seed/mock_logs/consumer.log",
    ]
    assert [document.document_type for document in documents] == ["runbook", "schema", "mock_log"]
    assert documents[0].title == "Retry Runbook"


def test_eval_case_parsing(tmp_path: Path) -> None:
    eval_dir = tmp_path / "seed" / "eval_cases"
    eval_dir.mkdir(parents=True)
    (eval_dir / "incident-triage-evals.json").write_text(
        json.dumps([{"id": "case-1", "name": "Case 1", "task": "Diagnose incident"}]),
        encoding="utf-8",
    )

    cases = load_eval_cases(tmp_path / "seed")

    assert cases == [{"id": "case-1", "name": "Case 1", "task": "Diagnose incident"}]


def test_seed_loader_is_idempotent(tmp_path: Path) -> None:
    seed_root = tmp_path / "seed"
    runbook = seed_root / "documents" / "runbooks" / "retry.md"
    eval_dir = seed_root / "eval_cases"
    runbook.parent.mkdir(parents=True)
    eval_dir.mkdir(parents=True)
    runbook.write_text("# Retry Runbook\nFirst version", encoding="utf-8")
    (eval_dir / "incident-triage-evals.json").write_text(
        json.dumps(
            [
                {
                    "id": "incident-1",
                    "name": "Kafka duplicate key",
                    "task": "Diagnose duplicate key",
                    "category": "incident_investigation",
                    "difficulty": "medium",
                    "risk_level": "medium",
                    "expected_capability": "evidence_based_root_cause_analysis",
                    "workflow_tags": ["kafka", "duplicate-key"],
                    "expected_keywords": ["duplicate key"],
                    "minimum_score": 70,
                }
            ]
        ),
        encoding="utf-8",
    )
    db = FakeSession()

    first_summary = load_seed_data(db, seed_root)
    runbook.write_text("# Retry Runbook\nSecond version", encoding="utf-8")
    second_summary = load_seed_data(db, seed_root)

    assert first_summary.knowledge_documents_created == 1
    assert first_summary.eval_cases_created == 1
    assert second_summary.knowledge_documents_updated == 1
    assert second_summary.eval_cases_updated == 1
    assert len(db.knowledge_documents) == 1
    assert len(db.eval_cases) == 1
    assert db.knowledge_documents["seed/documents/runbooks/retry.md"].content.endswith("Second version")
    assert db.eval_cases["Kafka duplicate key"].expected_signals["source_id"] == "incident-1"
    assert db.eval_cases["Kafka duplicate key"].expected_signals["category"] == "incident_investigation"
    assert db.eval_cases["Kafka duplicate key"].expected_signals["difficulty"] == "medium"
    assert db.eval_cases["Kafka duplicate key"].expected_signals["risk_level"] == "medium"
    assert (
        db.eval_cases["Kafka duplicate key"].expected_signals["expected_capability"]
        == "evidence_based_root_cause_analysis"
    )
    assert db.eval_cases["Kafka duplicate key"].expected_signals["workflow_tags"] == [
        "kafka",
        "duplicate-key",
    ]
    assert db.eval_cases["Kafka duplicate key"].tags == ["kafka", "duplicate-key"]
    assert db.commits == 2


def _where_value(where_clause: BinaryExpression) -> Any:
    return where_clause.right.value
