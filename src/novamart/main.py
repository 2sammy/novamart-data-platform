import json
from datetime import UTC, datetime
from pathlib import Path


def normalize_platform_name(platform_name: str) -> str:
    """Validate and normalize a data platform name."""
    if not isinstance(platform_name, str):
        raise TypeError("platform_name must be a string.")

    normalized_name = platform_name.strip()

    if normalized_name == "":
        raise ValueError("Please provide a platform name.")

    return normalized_name


def get_platform_status(platform_name: str) -> str:
    """Validate a platform name and return its running status.

    Args:
        platform_name: The name of the data platform.

    Returns:
        A message indicating that the data platform is running.

    Raises:
        TypeError: If platform_name is not a string.
        ValueError: If platform_name is empty or contains only whitespace.
    """
    normalized_name = normalize_platform_name(platform_name)

    return f"{normalized_name} data platform is running."


def create_platform_record(platform_name: str) -> dict[str, str]:
    """Create a structured status record for a data platform."""
    normalized_name = normalize_platform_name(platform_name)

    return {
        "platform_name": normalized_name,
        "status": "running",
    }


def create_platform_records(
    platform_names: list[str],
) -> list[dict[str, str]]:
    """Create structured status records for multiple data platforms."""
    if not isinstance(platform_names, list):
        raise TypeError("platform_names must be a list.")

    if not platform_names:
        raise ValueError("platform_names must not be empty.")

    records = []
    seen_names = set()

    for platform_name in platform_names:
        record = create_platform_record(platform_name)

        normalized_name = record["platform_name"]
        comparison_name = normalized_name.lower()

        if comparison_name in seen_names:
            raise ValueError(
                "platform_names must not contain duplicates."
            )

        seen_names.add(comparison_name)
        records.append(record)

    return records


def create_platform_batch(
    platform_names: list[str],
) -> dict[str, int | str | list[dict[str, str]]]:
    """Create platform records together with batch metadata.

    Args:
        platform_names: A non-empty list of unique platform names.

    Returns:
        A dictionary containing the processing timestamp, number of
        processed records, and the completed platform records.

    Raises:
        TypeError: If platform_names is not a list or contains
            a non-string value.
        ValueError: If the list is empty, contains a blank name,
            or contains duplicate names.
    """
    # Reuse the existing function so validation remains in one place.
    records = create_platform_records(platform_names)

    # Capture the exact time when this batch was processed in UTC.
    processed_at = datetime.now(UTC).isoformat()

    # Return the processing metadata together with the records.
    return {
        "record_count": len(records),
        "processed_at": processed_at,
        "records": records,
    }


def save_platform_batch(
    platform_names: list[str],
    output_path: str,
) -> None:
    """Create a platform batch and save it to a JSON file.

    Args:
        platform_names: A non-empty list of unique platform names.
        output_path: The file path where the JSON batch will be saved.

    Raises:
        TypeError: If platform_names is invalid or output_path is not a string.
        ValueError: If platform_names contains invalid values or output_path
            is empty.
    """
    if not isinstance(output_path, str):
        raise TypeError("output_path must be a string.")

    normalized_path = output_path.strip()

    if normalized_path == "":
        raise ValueError("output_path must not be empty.")

    # Create and validate the complete batch before writing any data.
    batch = create_platform_batch(platform_names)

    # Convert the supplied string path into a Path object.
    destination = Path(normalized_path)

    # Open the destination file and save the batch as formatted JSON.
    with destination.open("w", encoding="utf-8") as output_file:
        json.dump(batch, output_file, indent=4)


if __name__ == "__main__":
    status = get_platform_status("NovaMart")
    print(status)
