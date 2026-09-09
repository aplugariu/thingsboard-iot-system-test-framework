
import httpx


def test_login_returns_token_for_expected_user(
    api_client: httpx.Client, credentials: dict[str, str]
):
    login_response = api_client.post("/api/auth/login", json=credentials)

    assert login_response.status_code == 200, (
        f"Login: expected HTTP 200, got {login_response.status_code}"
    )

    token = login_response.json().get("token")
    if not isinstance(token, str) or not token.strip():
        raise AssertionError("Login response must contain a non-empty token")

    user_response = api_client.get(
        "/api/auth/user",
        headers={"X-Authorization": f"Bearer {token}"},
    )

    assert user_response.status_code == 200, (
        f"Current user: expected HTTP 200, got {user_response.status_code}"
    )

    user = user_response.json()
    assert user["email"] == credentials["username"]
    assert user["authority"] == "SYS_ADMIN"
