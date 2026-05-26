OPENAI_PRICING_USD_PER_1M_TOKENS: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-mini": (0.40, 1.60),
}


def estimate_openai_cost(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    pricing = OPENAI_PRICING_USD_PER_1M_TOKENS.get(model_name)
    if pricing is None:
        return 0.0

    input_price, output_price = pricing
    return ((input_tokens * input_price) + (output_tokens * output_price)) / 1_000_000
