from app.services.pricing import estimate_openai_cost


def test_estimate_openai_cost_uses_known_model_pricing() -> None:
    assert estimate_openai_cost("gpt-4o-mini", input_tokens=1000, output_tokens=2000) == 0.00135


def test_estimate_openai_cost_returns_zero_for_unknown_model() -> None:
    assert estimate_openai_cost("unknown-model", input_tokens=1000, output_tokens=2000) == 0.0
