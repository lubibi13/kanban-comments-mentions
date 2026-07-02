def test_register_login_create_and_list_task(client):
    # register
    r = client.post("/auth/register", json={"email": "alice@example.com", "password": "s3cret123"})
    assert r.status_code == 201, r.text
    # login (OAuth2 form)
    r = client.post("/auth/login", data={"username": "alice@example.com", "password": "s3cret123"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # create task
    r = client.post("/tasks/", json={"title": "Buy milk", "description": "2L whole", "status": "todo"}, headers=headers)
    assert r.status_code == 201, r.text
    task = r.json()
    assert task["title"] == "Buy milk"
    # list tasks
    r = client.get("/tasks/", headers=headers)
    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy milk"
