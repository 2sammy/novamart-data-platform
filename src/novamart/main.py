def get_platform_status(platform_name: str) -> str:
    if not isinstance(platform_name, str):
        raise TypeError("platform_name must be a string.")

    normalized_name = platform_name.strip()

    if normalized_name == "":
        raise ValueError("Please provide a platform name.")

    return f"{normalized_name} data platform is running."


if __name__ == "__main__":
    status = get_platform_status("NovaMart")
    print(status)
