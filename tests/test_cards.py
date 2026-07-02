def register_and_login(client, email, password):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_column_and_card_ownership_isolation(client):
    headers_a = register_and_login(client, "a@example.com", "s3cret123")
    headers_b = register_and_login(client, "b@example.com", "s3cret123")

    r = client.post("/boards/", json={"title": "A's Board"}, headers=headers_a)
    assert r.status_code == 201, r.text
    board_id = r.json()["id"]

    r = client.post(f"/boards/{board_id}/columns", json={"title": "To Do"}, headers=headers_a)
    assert r.status_code == 201, r.text
    column_id = r.json()["id"]

    r = client.post(f"/columns/{column_id}/cards", json={"title": "Card 1"}, headers=headers_a)
    assert r.status_code == 201, r.text
    card_id = r.json()["id"]

    # B is not the owner: every column/card route must 404
    r = client.patch(f"/columns/{column_id}", json={"title": "Hijacked"}, headers=headers_b)
    assert r.status_code == 404, r.text

    r = client.post(f"/columns/{column_id}/cards", json={"title": "Sneaky Card"}, headers=headers_b)
    assert r.status_code == 404, r.text

    r = client.patch(f"/cards/{card_id}", json={"title": "Hijacked"}, headers=headers_b)
    assert r.status_code == 404, r.text

    # even an attempt to move the card into another column must 404 for a non-owner
    r = client.patch(f"/cards/{card_id}", json={"column_id": column_id}, headers=headers_b)
    assert r.status_code == 404, r.text

    r = client.delete(f"/cards/{card_id}", headers=headers_b)
    assert r.status_code == 404, r.text

    r = client.delete(f"/columns/{column_id}", headers=headers_b)
    assert r.status_code == 404, r.text

    # A is the owner: all routes succeed
    r = client.patch(f"/columns/{column_id}", json={"title": "Renamed Column"}, headers=headers_a)
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Renamed Column"

    r = client.patch(f"/cards/{card_id}", json={"title": "Renamed Card"}, headers=headers_a)
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Renamed Card"

    r = client.delete(f"/cards/{card_id}", headers=headers_a)
    assert r.status_code == 204, r.text

    r = client.delete(f"/columns/{column_id}", headers=headers_a)
    assert r.status_code == 204, r.text
