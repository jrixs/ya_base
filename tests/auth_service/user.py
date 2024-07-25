import pytest
import httpx

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    "user_id, query_data, expected_status",
    [
        (1, {"limit": 10, "offset": 0}, 200),   # Valid request
        (1, {"limit": 0, "offset": 0}, 200),    # Valid request with limit 0
        (1, {"limit": -1, "offset": 0}, 422),   # Invalid limit
        (1, {"limit": 10, "offset": -1}, 422),  # Invalid offset
        (999, {"limit": 10, "offset": 0}, 404), # Nonexistent user
        # Add more test cases as needed
    ]
)
async def test_user_history(user_id, query_data, expected_status):
    url = f"http://127.0.0.1:4081/user/{user_id}/history"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = await client.get(url, params=query_data, headers=headers)

    assert response.status_code == expected_status, f"Unexpected response: {response.json()}"


@pytest.mark.parametrize(
    "user_id, update_data, expected_status",
    [
        (1, {"username": "new_username", "email": "new_email@example.com"}, 200),  # Valid update
        (1, {"username": "", "email": "new_email@example.com"}, 422),             # Invalid username
        (1, {"username": "new_username", "email": "not-an-email"}, 422),          # Invalid email
        (999, {"username": "new_username", "email": "new_email@example.com"}, 404), # Nonexistent user
        (1, {}, 200),                                                            # Valid but no changes
        # Add more test cases as needed
    ]
)
async def test_update_user(user_id, update_data, expected_status):
    url = f"http://127.0.0.1:4081/user/{user_id}"  

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = await client.put(url, json=update_data, headers=headers)
    
    assert response.status_code == expected_status, f"Unexpected response: {response.json()}"