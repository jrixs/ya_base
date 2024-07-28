import pytest
import httpx

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "user_id, expected_response",
    [
        (1, 200),  # Existing user
        (999, 404),  # Nonexistent user
        # Add more test cases as needed
    ],
)
async def test_get_user(user_id, expected_response):
    url = f"http://127.0.0.1:4081/admin/user/{user_id}"

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
        }
        response = await client.get(url, headers=headers)

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


# Test setting a role for a user
@pytest.mark.parametrize(
    "user_id, role_data, expected_response",
    [
        (1, {"name": "new_role"}, 200),  # Valid role assignment
        (1, {"name": ""}, 422),  # Invalid role name (empty)
        (999, {"name": "new_role"}, 404),  # Nonexistent user
        # Add more test cases as needed
    ],
)
async def test_set_user_role(user_id, role_data, expected_response):
    url = f"http://127.0.0.1:4081/admin/user/{user_id}/role/111"

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = await client.put(url, json=role_data, headers=headers)

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


# Test unsetting a role from a user
@pytest.mark.parametrize(
    "user_id, role_id, expected_response",
    [
        (1, 111, 204),  # Successful role removal
        (1, 999, 404),  # Nonexistent role
        (999, 111, 404),  # Nonexistent user
        # Add more test cases as needed
    ],
)
async def test_unset_user_role(user_id, role_id, expected_response):
    url = f"http://127.0.0.1:4081/admin/user/{user_id}/role/{role_id}"

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "*/*",
        }
        response = await client.delete(url, headers=headers)

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"
