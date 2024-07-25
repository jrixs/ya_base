import pytest
import httpx

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        ({"username": "user1", "email": "user1@example.com", "password": "password123"}, 200),  # Successful registration
        ({"username": "user1", "email": "user1@example.com", "password": "password123"}, {'status_code': 400, 'detail': 'User_already_exist', 'headers': None}),       # User exist
        ({"username": "user2", "email": "not-an-email", "password": "password123"}, {'status_code': 400, 'detail': 'invalid email', 'headers': None}),       # Invalid email
        # Add more test cases as needed
    ]
)
async def test_registration(query_data, expected_response):
    url = "http://127.0.0.1:4081/register"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = await client.post(url, data=query_data, headers=headers)

    try :
        assert response.status_code == expected_response
    except:
        assert response.json() == expected_response, f"Unexpected response: {response.json()}"

@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        ({"username": "user1", "password": "password123"}, 200),       # User exist
        ({"username": "user2", "password": "password123"}, {'detail': 'Invalid username or password'}), # Invalid Username
        ({"username": "user1", "password": "sss"}, {'detail': 'Invalid username or password'}), # Invalid Password
        # Add more test cases as needed
    ]
)
async def test_login(query_data, expected_response):
    url = "http://127.0.0.1:4081/login"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = await client.post(url, json=query_data, headers=headers)

    try :
        assert response.status_code == expected_response
    except:
        assert response.json() == expected_response, f"Unexpected response: {response.json()}"