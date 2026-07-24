import json
from datetime import datetime

import pytest

from src.novamart.main import create_platform_batch
from src.novamart.main import create_platform_record
from src.novamart.main import create_platform_records
from src.novamart.main import get_platform_status
from src.novamart.main import load_platform_batch
from src.novamart.main import load_platform_names_from_csv
from src.novamart.main import normalize_platform_name
from src.novamart.main import run_csv_platform_pipeline
from src.novamart.main import run_platform_pipeline
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


def test_run_platform_pipeline_saves_and_loads_batch(tmp_path):
    """Verify that the complete pipeline persists and reloads the batch."""

    # Create a temporary destination for the pipeline output.
    output_path = tmp_path / "pipeline_batch.json"

    # Run the complete workflow: validate, save, load, and return.
    result = run_platform_pipeline(
        ["NovaMart", "RetailHub"],
        str(output_path),
    )

    # Confirm that the pipeline created the JSON file on disk.
    assert output_path.exists()

    # Confirm that the reloaded batch reports the correct record count.
    assert result["record_count"] == 2

    # Confirm that the returned records came through the full pipeline.
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

    # Confirm that batch metadata was preserved during save and reload.
    assert "processed_at" in result


def test_load_platform_names_from_csv_reads_raw_names(tmp_path):
    """Verify that the CSV reader returns raw platform-name values."""

    # Create a temporary CSV file that pytest will remove automatically.
    input_path = tmp_path / "platforms.csv"

    # Write a header and two platform-name rows into the CSV file.
    input_path.write_text(
        "platform_name\n"
        " NovaMart \n"
        "RetailHub\n",
        encoding="utf-8",
    )

    # Read the platform names using the production CSV function.
    result = load_platform_names_from_csv(str(input_path))

    # Confirm that the reader returns raw values without normalization.
    assert result == [
        " NovaMart ",
        "RetailHub",
    ]


def test_load_platform_names_from_csv_rejects_missing_column(tmp_path):
    """Verify that a CSV without platform_name is rejected."""

    # Create a temporary path for a CSV with the wrong header.
    input_path = tmp_path / "platforms.csv"

    # Write a CSV that does not contain the required platform_name column.
    input_path.write_text(
        "name\n"
        "NovaMart\n"
        "RetailHub\n",
        encoding="utf-8",
    )

    # Confirm that the CSV reader stops with a clear validation error.
    with pytest.raises(
        ValueError,
        match="CSV file must contain a platform_name column.",
    ):
        load_platform_names_from_csv(str(input_path))


def test_load_platform_names_from_csv_rejects_invalid_csv(tmp_path):
    """Verify that malformed CSV content stops the ingestion process."""

    # Create a temporary path for a deliberately malformed CSV file.
    input_path = tmp_path / "invalid_platforms.csv"

    # Write an opening quotation mark without a matching closing mark.
    input_path.write_text(
        "platform_name\n"
        '"NovaMart\n'
        "RetailHub\n",
        encoding="utf-8",
    )

    # Confirm that the low-level CSV error becomes a clear pipeline error.
    with pytest.raises(
        ValueError,
        match="Input file contains invalid CSV",
    ):
        load_platform_names_from_csv(str(input_path))


def test_run_csv_platform_pipeline_processes_csv_to_json(tmp_path):
    """Verify that the complete CSV-to-JSON pipeline works successfully."""

    # Create temporary paths for the source CSV and destination JSON files.
    input_path = tmp_path / "platforms.csv"
    output_path = tmp_path / "platform_batch.json"

    # Write raw platform names into the temporary CSV file.
    input_path.write_text(
        "platform_name\n"
        " NovaMart \n"
        "RetailHub\n",
        encoding="utf-8",
    )

    # Run the full CSV extraction, transformation, and loading workflow.
    result = run_csv_platform_pipeline(
        str(input_path),
        str(output_path),
    )

    # Confirm that the pipeline created the destination JSON file.
    assert output_path.exists()

    # Confirm that both CSV rows were processed.
    assert result["record_count"] == 2

    # Confirm that the pipeline normalized the raw CSV values.
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

    # Confirm that the processing timestamp survived persistence and reload.
    assert "processed_at" in result


def test_load_platform_names_from_csv_rejects_header_only_file(tmp_path):
    """Verify that a CSV with no data rows is rejected."""

    # Create a temporary path for the CSV test file.
    input_path = tmp_path / "empty_platforms.csv"

    # Create a CSV containing the correct header but no platform records.
    input_path.write_text(
        "platform_name\n",
        encoding="utf-8",
    )

    # Confirm that the CSV reader rejects a file with no data rows.
    with pytest.raises(
        ValueError,
        match="CSV file must contain at least one platform record.",
    ):
        load_platform_names_from_csv(str(input_path))
