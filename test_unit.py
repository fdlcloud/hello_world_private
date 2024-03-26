from main import app, post_data_to_api, JSONResponse
import pytest
from fastapi.testclient import TestClient

"""
def override_dependency(q: str | None = None):
    return {"q": q, "skip": 5, "limit": 10}


def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


app.dependency_overrides[common_parameters] = override_dependency
"""

client = TestClient(app)


def test_post_data_to_api_success(mocker):
    """Tests successful API POST call with JSON data."""
    mock_response_data = {"success": True, "id": 1}
    # Correctly mock requests.post used within the app module
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response_data

    endpoint_url = "https://fakeapi.com/data"
    json_data = {"name": "Test Name", "value": "Test Value"}
    result = post_data_to_api(endpoint_url, json_data)

    assert result == mock_response_data
    mock_post.assert_called_once_with(endpoint_url, json=json_data)


def add(a, b):
    #Add two numbers
    return a + b


# The parameters are: a, b, expected
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),  # Simple case
    (-1, -1, -2),  # Negative numbers
    (1.5, 2.5, 4),  # Floating point numbers
    (0, 0, 0),  # Zeros
    (100000, 100000, 200000)  # Large numbers
])
def test_add(a, b, expected):
    assert add(a, b) == expected


def test_get_weather(mocker):
    # Mock the 'get_weather' function with pytest-mocker

    mock_post = mocker.patch('app.main.get_weather')
    mock_post.return_value.status_code = 707
    mocked_response = {
        "temperature": "22°C",
        "condition": "Sunny",
    }
    #mock_post.return_value.json = mocked_response
    #mock_post.json = mocked_response
    mock_post.return_value = JSONResponse(content=mocked_response)

    # Make a request to our FastAPI app
    response = client.get("/weather/London")

    # Assert the mock was called and the response is as expected
    assert mock_post.called
    print(mock_post.called)

    print('MM', response.status_code, response.json())

    assert response.status_code == 200
    assert sorted(response.json().items()) == sorted(mocked_response.items())


def test_read_root():
    # simple call test
    response = client.get("/root")
    print(response.status_code)
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}