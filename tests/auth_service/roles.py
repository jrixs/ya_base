import pytest
import httpx

pytestmark = pytest.mark.asyncio


# Test getting all roles
@pytest.mark.parametrize(
    "expected_response",
    [
        (200),  # Successful request
    ],
)
async def test_get_all_roles(expected_response):
    url = "http://127.0.0.1:4081/admin/role"

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


# Test creating a new role
@pytest.mark.parametrize(
    "role_data, expected_response",
    [
        ({"name": "new_role"}, 201),  # Valid role creation
        ({"name": ""}, 422),  # Invalid role name (empty)
        (
            {"name": "existing_role"},
            409,
        ),  # Role already exists (if applicable)
        # Add more test cases as needed
    ],
)
async def test_create_role(role_data, expected_response):
    url = "http://127.0.0.1:4081/admin/role"

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
        }
        response = await client.post(url, json=role_data, headers=headers)

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


# Test updating an existing role
@pytest.mark.parametrize(
    "role_id, role_data, expected_response",
    [
        (111, {"name": "updated_role"}, 200),  # Valid role update
        (111, {"name": ""}, 422),  # Invalid role name (empty)
        (999, {"name": "updated_role"}, 404),  # Nonexistent role
        # Add more test cases as needed
    ],
)
async def test_update_role(role_id, role_data, expected_response):
    url = f"http://127.0.0.1:4081/admin/role/{role_id}"

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


# Test deleting an existing role
@pytest.mark.parametrize(
    "role_id, expected_response",
    [
        (111, 204),  # Successful deletion
        (999, 404),  # Nonexistent role
        # Add more test cases as needed
    ],
)
async def test_delete_role(role_id, expected_response):
    url = f"http://127.0.0.1:4081/admin/role/{role_id}"

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
