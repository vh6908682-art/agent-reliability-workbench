from app.db.session import SessionLocal
from app.services.seed_loader import load_seed_data


def main() -> None:
    db = SessionLocal()
    try:
        summary = load_seed_data(db)
    finally:
        db.close()

    print(
        "Seed load complete: "
        f"{summary.knowledge_documents_loaded} knowledge documents loaded "
        f"({summary.knowledge_documents_created} created, {summary.knowledge_documents_updated} updated); "
        f"{summary.eval_cases_loaded} eval cases loaded "
        f"({summary.eval_cases_created} created, {summary.eval_cases_updated} updated)."
    )


if __name__ == "__main__":
    main()
