"""Approximate Claude pricing (USD per 1M tokens) — update when Anthropic changes rates."""

from app.agents.config import AgentModel

# March 2026 approximate public rates
PRICING_USD_PER_MILLION: dict[AgentModel, tuple[float, float]] = {
    AgentModel.SONNET: (3.0, 15.0),  # input, output
    AgentModel.HAIKU: (0.25, 1.25),
}


def tokens_to_cost_inr(
    model: AgentModel,
    input_tokens: int,
    output_tokens: int,
    usd_to_inr: float,
) -> float:
    input_rate, output_rate = PRICING_USD_PER_MILLION[model]
    usd = (input_tokens / 1_000_000) * input_rate + (
        output_tokens / 1_000_000
    ) * output_rate
    return round(usd * usd_to_inr, 4)
