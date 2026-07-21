import json
from datetime import datetime

import pytest

from src.novamart.main import create_platform_batch
from src.novamart.main import create_platform_record
from src.novamart.main import create_platform_records
from src.novamart.main import get_platform_status
from src.novamart.main import load_platform_batch
from src.novamart.main import normalize_platform_name
from src.novamart.main import save_platform_batch


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


def test_create_platform_batch_returns_valid_utc_timestamp():
    """Verify that the batch contains a valid UTC processing timestamp."""

    # Create a valid batch so the function generates processed_at.
    result = create_platform_batch(["NovaMart"])

    # Convert the ISO timestamp string back into a datetime object.
    processed_at = datetime.fromisoformat(result["processed_at"])

    # Confirm that the timestamp includes UTC timezone information.
    assert processed_at.utcoffset().total_seconds() == 0


def test_save_platform_batch_writes_valid_json_file(tmp_path):
    """Verify that a platform batch is saved as valid JSON."""

    # Create a temporary file path that pytest will remove automatically.
    output_path = tmp_path / "platform_batch.json"

    # Save a valid platform batch to the temporary JSON file.
    save_platform_batch(
        ["NovaMart", "RetailHub"],
        str(output_path),
    )

    # Open the saved file and convert its JSON content back to Python data.
    with output_path.open("r", encoding="utf-8") as input_file:
        saved_batch = json.load(input_file)

    # Confirm that the saved metadata reports two processed records.
    assert saved_batch["record_count"] == 2

    # Confirm that the saved records contain the expected platform data.
    assert saved_batch["records"] == [
        {
            "platform_name": "NovaMart",
            "status": "running",
        },
        {
            "platform_name": "RetailHub",
            "status": "running",
        },
    ]

    # Confirm that the JSON file contains a processing timestamp.
    assert "processed_at" in saved_batch


def test_load_platform_batch_reads_valid_json_file(tmp_path):
    """Verify that a saved JSON batch is loaded as Python data."""

    # Create a temporary JSON file path.
    input_path = tmp_path / "platform_batch.json"

    # Prepare known JSON data so we can verify the loaded result.
    expected_batch = {
        "record_count": 1,
        "processed_at": "2026-07-21T12:00:00+00:00",
        "records": [
            {
                "platform_name": "NovaMart",
                "status": "running",
            }
        ],
    }

    # Write the known batch into the temporary JSON file.
    with input_path.open("w", encoding="utf-8") as output_file:
        json.dump(expected_batch, output_file, indent=4)

    # Load the JSON file using the production function.
    loaded_batch = load_platform_batch(str(input_path))

    # Confirm that the loaded Python data matches the saved JSON data.
    assert loaded_batch == expected_batch


def test_load_platform_batch_rejects_invalid_json(tmp_path):
    """Verify that malformed JSON causes the pipeline to stop."""

    # Create a temporary path for a deliberately corrupted JSON file.
    input_path = tmp_path / "corrupted_batch.json"

    # Write incomplete JSON that cannot be converted into Python data.
    input_path.write_text(
        '{"record_count": 2, "records":',
        encoding="utf-8",
    )

    # Confirm that the loader stops with a clear validation error.
    with pytest.raises(
        ValueError,
        match="Input file contains invalid JSON",
    ):
        load_platform_batch(str(input_path))
