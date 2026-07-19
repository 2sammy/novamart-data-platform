from src.novamart.main import get_platform_status


def test_get_platform_status():
    assert get_platform_status("NovaMart") == "NovaMart data platform is running."


def test_get_platform_status_with_different_name():
    assert get_platform_status("RetailHub") == "RetailHub data platform is running."
