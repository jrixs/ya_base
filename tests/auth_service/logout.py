import pytest
import httpx

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        # ({}, 200),  # Successful logout
        ({}, {"detail": "Unauthorized"}),  # Unauthorized
    ],
)
async def test_logout(query_data, expected_response):
    url = "http://127.0.0.1:4081/auth/logout"  # Убедитесь, что это правильный URL

    async with httpx.AsyncClient() as client:
        headers = {
            "accept": "application/json",
        }
        response = await client.post(url, data=query_data, headers=headers)
    print(response.json())
    try:
        assert response.status_code == expected_response
    except:
        assert (
            response.json() == expected_response
        ), f"Unexpected response: {response.json()}"
