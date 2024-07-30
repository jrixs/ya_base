import pytest
import httpx

pytestmark = pytest.mark.asyncio

LOGIN_URL = "http://127.0.0.1:4081/auth/login"
LOGIN_CREDENTIALS = {"username": "user1", "password": "password123"}


# Test getting all roles
@pytest.mark.parametrize(
    "expected_response",
    [
        {"detail": "Access Denied"},  # Successful request
    ],
)
async def test_get_all_roles(expected_response):
    url = "http://127.0.0.1:4081/auth/admin/role"

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


# Test creating a new role
@pytest.mark.parametrize(
    "role_data, expected_response",
    [
        (
            {"name": "new_role"},
            {"detail": "Access Denied"},
        ),  # Valid role creation
        (
            {"name": ""},
            {"detail": "Access Denied"},
        ),  # Invalid role name (empty)
        (
            {"name": "existing_role"},
            {"detail": "Access Denied"},
        ),  # Role already exists (if applicable)
        # Add more test cases as needed
    ],
)
async def test_create_role(role_data, expected_response):
    url = "http://127.0.0.1:4081/auth/admin/role"

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
            url, cookies=cookies, headers={"accept": "application/json"}
        )

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"


# Test updating an existing role
@pytest.mark.parametrize(
    "role_id, expected_response",
    [
        (111, {"detail": "Access Denied"}),  # Valid role update
        (111, {"detail": "Access Denied"}),  # Invalid role name (empty)
        # Add more test cases as needed
    ],
)
async def test_update_role(role_id, expected_response):
    url = f"http://127.0.0.1:4081/auth/admin/role/{role_id}"

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
            url, cookies=cookies, headers={"accept": "application/json"}
        )

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
        (111, {"detail": "Access Denied"}),  # Successful deletion
        (999, {"detail": "Access Denied"}),  # Nonexistent role
        # Add more test cases as needed
    ],
)
async def test_delete_role(role_id, expected_response):
    url = f"http://127.0.0.1:4081/auth/admin/role/{role_id}"

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

        response = await client.delete(
            url, cookies=cookies, headers={"accept": "application/json"}
        )

    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"
