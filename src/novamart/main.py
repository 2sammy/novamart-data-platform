def get_platform_status(platform_name):
    return f"{platform_name} data platform is running."


if __name__ == "__main__":
    status = get_platform_status("NovaMart")
    print(status)
