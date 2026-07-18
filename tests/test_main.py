from src.novamart.main import get_platform_status


def test_get_platform_status():
    assert get_platform_status() == "NovaMart data platform is running."
