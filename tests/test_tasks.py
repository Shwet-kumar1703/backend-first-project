from fastapi import status
from fastapi.testclient import TestClient


def get_auth_header(
    client: TestClient, email: str, password: str = "password123"
) -> dict[str, str]:
    """Helper function to register, login, and return authorization bearer header."""
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_task(client: TestClient) -> None:
    """Test task creation for authenticated user."""
    headers = get_auth_header(client, "user@example.com")
    response = client.post(
        "/tasks",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "due_date": "2026-10-15",
        },
        headers=headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["due_date"] == "2026-10-15"
    assert data["is_completed"] is False
    assert "id" in data
    assert "owner_id" in data


def test_get_tasks_list(client: TestClient) -> None:
    """Test retrieving list of tasks belonging to authenticated user, newest first."""
    headers = get_auth_header(client, "user@example.com")
    client.post("/tasks", json={"title": "Task 1"}, headers=headers)
    client.post("/tasks", json={"title": "Task 2"}, headers=headers)

    response = client.get("/tasks", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 2"
    assert data[1]["title"] == "Task 1"


def test_get_single_task(client: TestClient) -> None:
    """Test retrieving a single task by ID for task owner."""
    headers = get_auth_header(client, "user@example.com")
    created = client.post(
        "/tasks", json={"title": "Single Task"}, headers=headers
    ).json()
    task_id = created["id"]

    response = client.get(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Single Task"


def test_update_task(client: TestClient) -> None:
    """Test updating task attributes."""
    headers = get_auth_header(client, "user@example.com")
    created = client.post(
        "/tasks", json={"title": "Original Title"}, headers=headers
    ).json()
    task_id = created["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "description": "New Desc"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "New Desc"


def test_complete_task(client: TestClient) -> None:
    """Test marking a task as completed."""
    headers = get_auth_header(client, "user@example.com")
    created = client.post(
        "/tasks", json={"title": "Incomplete Task"}, headers=headers
    ).json()
    task_id = created["id"]

    response = client.patch(f"/tasks/{task_id}/complete", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_completed"] is True


def test_delete_task(client: TestClient) -> None:
    """Test deleting a task."""
    headers = get_auth_header(client, "user@example.com")
    created = client.post(
        "/tasks", json={"title": "To Delete"}, headers=headers
    ).json()
    task_id = created["id"]

    del_resp = client.delete(f"/tasks/{task_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    get_resp = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_unauthenticated_access(client: TestClient) -> None:
    """Test that accessing tasks endpoints without token returns 401."""
    assert client.get("/tasks").status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        client.post("/tasks", json={"title": "Task"}).status_code
        == status.HTTP_401_UNAUTHORIZED
    )
    assert client.get("/tasks/1").status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        client.put("/tasks/1", json={"title": "Task"}).status_code
        == status.HTTP_401_UNAUTHORIZED
    )
    assert (
        client.patch("/tasks/1/complete").status_code
        == status.HTTP_401_UNAUTHORIZED
    )
    assert client.delete("/tasks/1").status_code == status.HTTP_401_UNAUTHORIZED


def test_user_isolation(client: TestClient) -> None:
    """Test that User B cannot read, update, complete, or delete User A's task (404)."""
    headers_a = get_auth_header(client, "usera@example.com")
    headers_b = get_auth_header(client, "userb@example.com")

    # User A creates a task
    task_a = client.post(
        "/tasks", json={"title": "User A Task"}, headers=headers_a
    ).json()
    task_id = task_a["id"]

    # User B tries to access User A's task -> 404
    get_resp = client.get(f"/tasks/{task_id}", headers=headers_b)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
    assert get_resp.json()["detail"] == "Task not found"

    # User B tries to update User A's task -> 404
    put_resp = client.put(
        f"/tasks/{task_id}", json={"title": "Hacked"}, headers=headers_b
    )
    assert put_resp.status_code == status.HTTP_404_NOT_FOUND
    assert put_resp.json()["detail"] == "Task not found"

    # User B tries to complete User A's task -> 404
    patch_resp = client.patch(f"/tasks/{task_id}/complete", headers=headers_b)
    assert patch_resp.status_code == status.HTTP_404_NOT_FOUND
    assert patch_resp.json()["detail"] == "Task not found"

    # User B tries to delete User A's task -> 404
    del_resp = client.delete(f"/tasks/{task_id}", headers=headers_b)
    assert del_resp.status_code == status.HTTP_404_NOT_FOUND
    assert del_resp.json()["detail"] == "Task not found"

    # Confirm User A's task is still intact
    confirm_a = client.get(f"/tasks/{task_id}", headers=headers_a)
    assert confirm_a.status_code == status.HTTP_200_OK
    assert confirm_a.json()["title"] == "User A Task"
