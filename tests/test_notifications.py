from app.models import User
from app.mentions import find_mentioned_users


def register_and_login(client, email, password):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_card(client, headers):
    r = client.post("/boards/", json={"title": "Board"}, headers=headers)
    assert r.status_code == 201, r.text
    board_id = r.json()["id"]

    r = client.post(f"/boards/{board_id}/columns", json={"title": "Column"}, headers=headers)
    assert r.status_code == 201, r.text
    column_id = r.json()["id"]

    r = client.post(f"/columns/{column_id}/cards", json={"title": "Card"}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_comment_mention_creates_unread_notification_for_mentioned_user(client):
    headers_a = register_and_login(client, "a@example.com", "s3cret123")
    headers_b = register_and_login(client, "b@example.com", "s3cret123")
    card_id = create_card(client, headers_a)

    r = client.post(f"/cards/{card_id}/comments", json={"body": "heads up @b"}, headers=headers_a)
    assert r.status_code == 201, r.text

    r = client.get("/notifications", headers=headers_b)
    assert r.status_code == 200, r.text
    notifications = r.json()
    assert len(notifications) == 1
    assert notifications[0]["read"] is False


def test_comment_without_mention_creates_no_notification(client):
    headers_a = register_and_login(client, "a@example.com", "s3cret123")
    headers_b = register_and_login(client, "b@example.com", "s3cret123")
    card_id = create_card(client, headers_a)

    r = client.post(f"/cards/{card_id}/comments", json={"body": "no mentions in this one"}, headers=headers_a)
    assert r.status_code == 201, r.text

    r = client.get("/notifications", headers=headers_b)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_comment_mentioning_unknown_user_creates_no_notification(client):
    headers_a = register_and_login(client, "a@example.com", "s3cret123")
    headers_b = register_and_login(client, "b@example.com", "s3cret123")
    card_id = create_card(client, headers_a)

    r = client.post(f"/cards/{card_id}/comments", json={"body": "cc @nobody"}, headers=headers_a)
    assert r.status_code == 201, r.text

    r = client.get("/notifications", headers=headers_b)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_find_mentioned_users_returns_known_and_skips_unknown(session):
    alice = User(email="alice@example.com", username="alice", hashed_password="x")
    bob = User(email="bob@example.com", username="bob", hashed_password="x")
    session.add(alice)
    session.add(bob)
    session.commit()
    session.refresh(alice)
    session.refresh(bob)

    found = find_mentioned_users("hey @alice and @nobody, cc @bob", session)

    assert {u.email for u in found} == {"alice@example.com", "bob@example.com"}
