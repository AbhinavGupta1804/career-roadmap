"""Force deterministic agent mocks during tests (no live Anthropic calls)."""

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def _agent_mock_mode_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_MOCK_MODE", "true")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
