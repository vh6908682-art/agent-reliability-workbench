from app.services.context_retriever import SeedContextRetriever


def test_context_retriever_finds_golden_path_context() -> None:
    retriever = SeedContextRetriever()

    results = retriever.retrieve(
        "A Kafka consumer failed while processing a customer update event. "
        "Logs show duplicate key violation and retry exhaustion."
    )

    source_paths = [result.source_path for result in results]
    assert "seed/documents/runbooks/duplicate-key-violations.md" in source_paths
    assert "seed/documents/runbooks/kafka-consumer-failures.md" in source_paths
    assert any(result.document_type == "schema" for result in results)
    assert results == sorted(results, key=lambda result: (-result.relevance_score, result.source_path))


def test_context_retriever_limits_results() -> None:
    retriever = SeedContextRetriever(max_results=2)

    results = retriever.retrieve("duplicate key retry exhaustion customer update")

    assert len(results) == 2
    assert all(result.relevance_score > 0 for result in results)
