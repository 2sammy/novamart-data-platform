import pytest

from src.novamart.main import create_platform_record
from src.novamart.main import get_platform_status


def test_get_platform_status():
    assert get_platform_status("NovaMart") == "NovaMart data platform is running."


def test_get_platform_status_with_different_name():
    assert get_platform_status("RetailHub") == "RetailHub data platform is running."


def test_get_platform_status_rejects_empty_name():
    with pytest.raises(ValueError, match="Please provide a platform name."):
        get_platform_status("")


def test_get_platform_status_rejects_whitespace_name():
    with pytest.raises(ValueError, match="Please provide a platform name."):
        get_platform_status("   ")


def test_get_platform_status_strips_surrounding_whitespace():
    assert get_platform_status(" NovaMart ") == "NovaMart data platform is running."


def test_get_platform_status_rejects_non_string_name():
    with pytest.raises(TypeError, match="platform_name must be a string."):
        get_platform_status(123)


def test_create_platform_record():
    assert create_platform_record("NovaMart") == {
        "platform_name": "NovaMart",
        "status": "running",
    }


def test_create_platform_record_rejects_whitespace_name():
    with pytest.raises(ValueError, match="Please provide a platform name."):
        create_platform_record("   ")
