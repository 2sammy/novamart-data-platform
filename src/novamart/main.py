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
) -> dict[str, int | list[dict[str, str]]]:
    """Create platform records together with batch metadata.

    Args:
        platform_names: A non-empty list of unique platform names.

    Returns:
        A dictionary containing the number of processed records
        and the completed platform records.

    Raises:
        TypeError: If platform_names is not a list or contains
            a non-string value.
        ValueError: If the list is empty, contains a blank name,
            or contains duplicate names.
    """
    # Reuse the existing batch function so all validation rules
    # remain in one place.
    records = create_platform_records(platform_names)

    # Return both the processed records and their total count.
    return {
        "record_count": len(records),
        "records": records,
    }


if __name__ == "__main__":
    status = get_platform_status("NovaMart")
    print(status)
