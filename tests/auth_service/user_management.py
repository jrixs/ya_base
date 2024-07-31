import pytest
import httpx

pytestmark = pytest.mark.asyncio

LOGIN_URL = "http://127.0.0.1:4081/auth/login"
LOGIN_CREDENTIALS = {"username": "user1", "password": "password123"}


@pytest.mark.parametrize(
    "user_id, expected_response",
    [
        (1, 404),
        (999, {"detail": "Not Found"}),
    ],
)
async def test_get_user(user_id, expected_response):
    url = f"http://127.0.0.1:4081/admin/user/"

    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            LOGIN_URL,
            json=LOGIN_CREDENTIALS,
            headers={"accept": "application/json"},
        )

        assert (
            login_response.status_code == 200
        ), f"Login failed: {login_response.json()}"

        cookies = login_response.cookies

        response = await client.get(
            url, cookies=cookies, headers={"accept": "application/json"}
        )

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


# Test setting a role for a user
@pytest.mark.parametrize(
    "params, expected_response",
    [
        ({"user_id": 1, "role_id": 999}, 307),
        ({"user_id": 1, "role_id": 999}, 307),
        ({"user_id": 1, "role_id": 999}, 307),
    ],
)
async def test_put_user(params, expected_response):
    url = f"http://127.0.0.1:4081/auth/admin/user/role/"

    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            LOGIN_URL,
            json=LOGIN_CREDENTIALS,
            headers={"accept": "application/json"},
        )

        assert (
            login_response.status_code == 200
        ), f"Login failed: {login_response.json()}"

        cookies = login_response.cookies

        response = await client.put(
            url,
            cookies=cookies,
            params=params,
            headers={"accept": "application/json"},
        )

    assert response.status_code == expected_response
