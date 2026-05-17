"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/ -q"""
from app.services.data_registry import validate_seed_data


def test_seed_data_is_consistent() -> None:
    status = validate_seed_data()
    assert status["data_valid"] is True
    assert status["careers_count"] == 60
    assert status["jd_roles_count"] == 20
    assert status["jd_total_count"] == 1000
