import requests
from starlette import status

BASE_URL = "http://0.0.0.0:8000"


def test_user_dependency():
    url = BASE_URL + "/users/me"
    response = requests.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_user():
    url = BASE_URL + "/users/register"
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "jj@example.com",
        "password": "string",
        "role": "presenter",
    }

    response = requests.post(url, json=data)
    assert response.status_code == status.HTTP_201_CREATED

def test_create_user_invalid():
    url = BASE_URL + "/users/register"
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "jj",
        "password": "string",
        "role": "presenter",
    }

    response = requests.post(url, json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


if __name__ == "__main__":
    test_user_dependency()
