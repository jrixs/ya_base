import pytest
import httpx

pytestmark = pytest.mark.asyncio

# Define the login URL and credentials
LOGIN_URL = "http://127.0.0.1:4081/auth/login"
LOGIN_CREDENTIALS = {"username": "user1", "password": "password123"}


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        ({}, 200),  # Valid request
        # Add more test cases as needed
    ],
)
async def test_user_info(query_data, expected_response):
    url = (
        f"http://127.0.0.1:4081/auth/user"  # Убедитесь, что это правильный URL
    )

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


@pytest.mark.parametrize(
    "update_data, expected_response",
    [
        (
            {
                "username": "new_username",
                "email": "new_email@example.com",
                "password": "string",
            },
            307,
        ),
    ],
)
async def test_update_user(update_data, expected_response):
    url = f"http://127.0.0.1:4081/auth/user/"

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

        response = await client.post(
            url,
            params=update_data,
            cookies=cookies,
            headers={"accept": "application/json"},
        )

    assert response.status_code == expected_response


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {
                "limit": 1,
                "offset": 10,
            },
            200,
        ),
        (
            {
                "limit": 5,
                "offset": 1,
            },
            200,
        ),
        (
            {
                "limit": -1,
                "offset": 10,
            },
            422,
        ),
        (
            {
                "limit": 4,
                "offset": -1,
            },
            422,
        ),
    ],
)
async def test_get_history(query_data, expected_response):
    url = "http://127.0.0.1:4081/auth/history"

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

        # Convert query_data to query parameters
        response = await client.get(
            url,
            params=query_data,
            cookies=cookies,
            headers={"accept": "application/json"},
        )

    print(response)

    assert response.status_code == expected_response
