import pytest

from src.novamart.main import create_platform_batch
from src.novamart.main import create_platform_record
from src.novamart.main import create_platform_records
from src.novamart.main import get_platform_status
from src.novamart.main import normalize_platform_name


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


def test_create_platform_record_rejects_non_string_name():
    with pytest.raises(TypeError, match="platform_name must be a string."):
        create_platform_record(123)


def test_normalize_platform_name_strips_surrounding_whitespace():
    assert normalize_platform_name("  RetailHub  ") == "RetailHub"


def test_create_platform_records():
    assert create_platform_records(["NovaMart", "RetailHub"]) == [
        {
            "platform_name": "NovaMart",
            "status": "running",
        },
        {
            "platform_name": "RetailHub",
            "status": "running",
        },
    ]


def test_create_platform_records_rejects_invalid_name():
    with pytest.raises(
        ValueError,
        match="Please provide a platform name.",
    ):
        create_platform_records(["NovaMart", "   ", "RetailHub"])


def test_create_platform_records_rejects_non_list_input():
    with pytest.raises(
        TypeError,
        match="platform_names must be a list.",
    ):
        create_platform_records("NovaMart")


def test_create_platform_records_rejects_empty_list():
    with pytest.raises(
        ValueError,
        match="platform_names must not be empty.",
    ):
        create_platform_records([])


def test_create_platform_records_rejects_duplicate_names():
    with pytest.raises(
        ValueError,
        match="platform_names must not contain duplicates.",
    ):
        create_platform_records(
            ["NovaMart", "  NovaMart  ", "RetailHub"]
        )


def test_create_platform_records_rejects_case_insensitive_duplicates():
    with pytest.raises(
        ValueError,
        match="platform_names must not contain duplicates.",
    ):
        create_platform_records(
            ["NovaMart", "novamart", "RetailHub"]
        )


def test_create_platform_batch_returns_records_and_count():
    """Verify that batch metadata contains the correct count and records."""

    # Arrange and Act:
    # Send two valid platform names to the batch-summary function.
    result = create_platform_batch(
        ["NovaMart", "RetailHub"]
    )

    # Assert:
    # Confirm that the reported count matches the two processed records.
    assert result["record_count"] == 2

    # Confirm that the returned records contain the expected
    # normalized platform names and running statuses.
    assert result["records"] == [
        {
            "platform_name": "NovaMart",
            "status": "running",
        },
        {
            "platform_name": "RetailHub",
            "status": "running",
        },
    ]
