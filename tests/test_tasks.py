def register_and_login(client, email, password):
    client.post("/signup", json={"email": email, "password": password})
    response = client.post("/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_tasks_only_own(client):
    headers1 = register_and_login(client, "vivek@gmail.com", "pass123")
    client.post("/tasks/", json={"title": "User1 task"}, headers=headers1)

    headers2 = register_and_login(client, "user2@example.com", "pass123")
    response = client.get("/tasks/", headers=headers2)

    assert response.status_code == 200
    assert response.json() == []  # user2 sees nothing


def test_cannot_access_other_users_task(client):
    headers1 = register_and_login(client, "owner@example.com", "pass123")
    create_response = client.post("/tasks/", json={"title": "Owner's task"}, headers=headers1)
    task_id = create_response.json()["id"]

    headers2 = register_and_login(client, "intruder@example.com", "pass123")
    response = client.get(f"/tasks/{task_id}", headers=headers2)

    assert response.status_code == 403


def test_cannot_delete_other_users_task(client):
    headers1 = register_and_login(client, "owner2@example.com", "pass123")
    create_response = client.post("/tasks/", json={"title": "Protected task"}, headers=headers1)
    task_id = create_response.json()["id"]

    headers2 = register_and_login(client, "intruder2@example.com", "pass123")
    response = client.delete(f"/tasks/{task_id}", headers=headers2)

    assert response.status_code == 403


def test_task_not_found_returns_404(client):
    headers = register_and_login(client, "nonexistent@example.com", "pass123")
    response = client.get("/tasks/99999", headers=headers)
    assert response.status_code == 404