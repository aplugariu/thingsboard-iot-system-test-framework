
import os

import httpx
import pytest


@pytest.fixture
def api_client():
    base_url = os.getenv("TB_BASE_URL", "http://localhost:8080")
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def credentials():
    username = os.getenv("TB_USERNAME")
    password = os.getenv("TB_PASSWORD")
    if not username or not password:
        pytest.fail("Set TB_USERNAME and TB_PASSWORD before running the test.")
    return {"username": username, "password": password}
