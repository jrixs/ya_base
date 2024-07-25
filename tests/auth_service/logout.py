import pytest
import httpx

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_status",
    [
        ({}, 200),  # Successful logout
    ]
)
async def test_logout(query_data, expected_status):
    url = "http://127.0.0.1:4081/logout"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
        }
        response = await client.post(url, data=query_data, headers=headers)

    assert response.status_code == expected_status, f"Unexpected response: {response.json()}"