def register_and_login(client, email, password):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_board_ownership_isolation(client):
    headers_a = register_and_login(client, "a@example.com", "s3cret123")
    headers_b = register_and_login(client, "b@example.com", "s3cret123")

    r = client.post("/boards/", json={"title": "A's Board"}, headers=headers_a)
    assert r.status_code == 201, r.text
    board_id = r.json()["id"]

    # B is not the owner: every route must 404, never reveal the board exists
    r = client.get(f"/boards/{board_id}", headers=headers_b)
    assert r.status_code == 404, r.text

    r = client.patch(f"/boards/{board_id}", json={"title": "Hijacked"}, headers=headers_b)
    assert r.status_code == 404, r.text

    r = client.delete(f"/boards/{board_id}", headers=headers_b)
    assert r.status_code == 404, r.text

    # A is the owner: all routes succeed
    r = client.get(f"/boards/{board_id}", headers=headers_a)
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "A's Board"

    r = client.patch(f"/boards/{board_id}", json={"title": "Renamed"}, headers=headers_a)
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Renamed"

    r = client.delete(f"/boards/{board_id}", headers=headers_a)
    assert r.status_code == 204, r.text
