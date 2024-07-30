import pytest
import httpx

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "password123",
            },
            200,
        ),  # Successful registration
        (
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "password123",
            },
            {"detail": "User_already_exist"},
        ),  # User exist
        (
            {
                "username": "user2",
                "email": "not-an-email",
                "password": "password123",
            },
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: An email address must have an @-sign.",
                        "input": "not-an-email",
                        "ctx": {
                            "reason": "An email address must have an @-sign."
                        },
                    }
                ]
            },
        ),  # Invalid email
    ],
)
async def test_registration(query_data, expected_response):
    url = "http://127.0.0.1:4081/auth/register"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = await client.post(url, json=query_data, headers=headers)

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"username": "user2", "password": "password123"},
            {"detail": "Invalid username or password"},
        ),  # Invalid Username
        (
            {"username": "user1", "password": "sss"},
            {"detail": "Invalid username or password"},
        ),  # Invalid Password
        ({"username": "user1", "password": "password123"}, 200),  # User exist
        # Add more test cases as needed
    ],
)
async def test_login(query_data, expected_response):
    url = (
        "http://127.0.0.1:4081/auth/login"  # Убедитесь, что это правильный URL
    )

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = await client.post(url, json=query_data, headers=headers)

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        # ({}, 200),  # Successful logout
        ({}, {"detail": "Unauthorized"}),  # Unauthorized
    ],
)
async def test_bad_logout(query_data, expected_response):
    url = "http://127.0.0.1:4081/auth/logout"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
        }
        response = await client.post(url, data=query_data, headers=headers)
    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


# Define the login URL and credentials
LOGIN_URL = "http://127.0.0.1:4081/auth/login"
LOGOUT_URL = "http://127.0.0.1:4081/auth/logout"
LOGIN_CREDENTIALS = {"username": "user1", "password": "password123"}


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        ({}, 200),
    ],
)
async def test_logout(query_data, expected_response):
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
            LOGOUT_URL,
            data=query_data,
            cookies=cookies,
            headers={"accept": "application/json"},
        )

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"
