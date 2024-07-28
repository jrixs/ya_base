import pytest
import httpx

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        ({"limit": 10, "offset": 0}, 200),  # Valid request
        ({"limit": 0, "offset": 0}, 200),  # Valid request with limit 0
        ({"limit": -1, "offset": 0}, 422),  # Invalid limit
        ({"limit": 10, "offset": -1}, 422),  # Invalid offset
        ({"limit": 10, "offset": 0}, 404),  # Nonexistent user
        # Add more test cases as needed
    ],
)
async def test_user_history(query_data, expected_response):
    url = f"http://127.0.0.1:4081/auth/user"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
        }
        response = await client.get(url, params=query_data, headers=headers)

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
            {"username": "new_username", "email": "new_email@example.com", "password": "string"},
            200,
        ),  # Valid update
        (
            {"username": "", "email": "new_email@example.com", "password": "string"},
            307,
        ),  # Invalid username
        (
            {"username": "new_username", "email": "not-an-email", "password": "string"},
            307,
        ),  # Invalid email
        (
            {"username": "new_username", "email": "new_email@example.com", "password": "string"},
            307,
        ),  # Nonexistent user
        ({}, 307),  # Valid but no changes
        # Add more test cases as needed
    ],
)
async def test_update_user(update_data, expected_response):
    url = f"http://127.0.0.1:4081/auth/user/"

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = await client.put(url, json=update_data, headers=headers)

    print(response)
    assert response.status_code == expected_response
    '''
    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"
    '''