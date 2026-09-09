import httpx
import pytest


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"X-Authorization": "Bearer not-a-valid-jwt"},
    ],
    ids=["missing-token", "malformed-token"],
)
def test_current_user_rejects_unauthenticated_request(
    api_client: httpx.Client, headers: dict[str, str]
):
    response = api_client.get("/api/auth/user", headers=headers)

    assert response.status_code == 401, (
        f"Expected HTTP 401, got {response.status_code}; "
        f"response body: {response.text[:500]}"
    )
