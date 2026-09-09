
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


@pytest.fixture
def tenant_api_client(api_client):
    username = os.getenv("TB_TENANT_USERNAME")
    password = os.getenv("TB_TENANT_PASSWORD")
    if not username or not password:
        pytest.fail("Set TB_TENANT_USERNAME and TB_TENANT_PASSWORD.")

    response = api_client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, (
        f"Tenant login failed: HTTP {response.status_code}"
    )

    token = response.json().get("token")
    if not isinstance(token, str) or not token.strip():
        pytest.fail("Tenant login did not return a valid token.")

    api_client.headers["X-Authorization"] = f"Bearer {token}"

    identity = api_client.get("/api/auth/user")
    assert identity.status_code == 200
    user = identity.json()
    assert user["email"] == username
    assert user["authority"] == "TENANT_ADMIN"

    return api_client


@pytest.fixture
def devices(tenant_api_client):
    from framework.api.devices import Devices

    return Devices(tenant_api_client)
