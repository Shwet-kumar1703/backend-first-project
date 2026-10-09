from fastapi import status
from fastapi.testclient import TestClient


def test_register_success(client: TestClient) -> None:
    """Test successful user registration with lowercased email."""
    response = client.post(
        "/auth/register",
        json={"email": "NewUser@Example.com", "password": "password123"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@example.com"
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient) -> None:
    """Test registration failure when email is already registered."""
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "USER@example.com", "password": "password123"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


def test_register_short_password(client: TestClient) -> None:
    """Test registration failure when password length is under 8 characters."""
    response = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client: TestClient) -> None:
    """Test successful login returning JWT access token."""
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "LOGIN@example.com", "password": "password123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient) -> None:
    """Test login failure with wrong password returning 401."""
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_email(client: TestClient) -> None:
    """Test login failure with unregistered email returning 401."""
    response = client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"
