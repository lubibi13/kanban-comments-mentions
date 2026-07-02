def register(client, email, password):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text


def login_via_form(client, email, password):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=False)


def create_board_column_card(client, board_title="Board", column_title="Column", card_title="Card"):
    r = client.post("/boards/", json={"title": board_title})
    assert r.status_code == 201, r.text
    board_id = r.json()["id"]

    r = client.post(f"/boards/{board_id}/columns", json={"title": column_title})
    assert r.status_code == 201, r.text
    column_id = r.json()["id"]

    r = client.post(f"/columns/{column_id}/cards", json={"title": card_title})
    assert r.status_code == 201, r.text
    card_id = r.json()["id"]

    return board_id, column_id, card_id


def test_login_page_renders_form(client):
    r = client.get("/login")
    assert r.status_code == 200, r.text
    assert 'name="email"' in r.text
    assert 'name="password"' in r.text


def test_login_with_valid_credentials_sets_cookie_and_redirects(client):
    register(client, "a@example.com", "s3cret123")

    r = login_via_form(client, "a@example.com", "s3cret123")

    assert r.status_code == 303, r.text
    assert "access_token" in r.cookies


def test_login_with_invalid_credentials_does_not_set_cookie(client):
    register(client, "a@example.com", "s3cret123")

    r = login_via_form(client, "a@example.com", "wrong-password")

    assert r.status_code == 401, r.text
    assert "access_token" not in r.cookies


def test_board_page_requires_authentication(client):
    r = client.get("/boards/1", headers={"Accept": "text/html"})
    assert r.status_code == 401, r.text


def test_board_page_renders_columns_cards_and_nav(client):
    register(client, "a@example.com", "s3cret123")
    login_via_form(client, "a@example.com", "s3cret123")
    board_id, column_id, card_id = create_board_column_card(client, card_title="Buy milk")

    r = client.get(f"/boards/{board_id}", headers={"Accept": "text/html"})
    assert r.status_code == 200, r.text
    assert "Column" in r.text
    assert "Buy milk" in r.text
    assert "Notifications (0)" in r.text


def test_board_json_route_is_unaffected_by_html_page(client):
    r = client.post("/auth/register", json={"email": "a@example.com", "password": "s3cret123"})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": "a@example.com", "password": "s3cret123"})
    token = r.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/boards/", json={"title": "Board"}, headers=auth_headers)
    board_id = r.json()["id"]

    r = client.get(f"/boards/{board_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Board"


def test_card_detail_page_renders_comment_with_mention_link_and_move_dropdown(client):
    register(client, "a@example.com", "s3cret123")
    register(client, "b@example.com", "s3cret123")
    login_via_form(client, "a@example.com", "s3cret123")

    board_id, column_id, card_id = create_board_column_card(client)
    r = client.post(f"/boards/{board_id}/columns", json={"title": "Doing"})
    assert r.status_code == 201, r.text
    other_column_id = r.json()["id"]

    r = client.post(f"/cards/{card_id}/comments", json={"body": "heads up @b"})
    assert r.status_code == 201, r.text

    r = client.get(f"/cards/{card_id}")
    assert r.status_code == 200, r.text
    assert 'href="/users/b"' in r.text
    assert "heads up" in r.text
    assert f'value="{other_column_id}"' in r.text
    assert "<select" in r.text


def test_card_comment_form_submission_creates_comment_and_redirects(client):
    register(client, "a@example.com", "s3cret123")
    login_via_form(client, "a@example.com", "s3cret123")
    board_id, column_id, card_id = create_board_column_card(client)

    r = client.post(
        f"/cards/{card_id}/comments/form",
        data={"body": "posted from the html form"},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text
    assert r.headers["location"] == f"/cards/{card_id}"

    r = client.get(f"/cards/{card_id}")
    assert "posted from the html form" in r.text


def test_notifications_feed_lists_unread_and_open_link_marks_read(client):
    register(client, "a@example.com", "s3cret123")
    register(client, "b@example.com", "s3cret123")
    login_via_form(client, "a@example.com", "s3cret123")

    board_id, column_id, card_id = create_board_column_card(client)
    r = client.post(f"/cards/{card_id}/comments", json={"body": "hi @b"})
    assert r.status_code == 201, r.text

    login_via_form(client, "b@example.com", "s3cret123")

    r = client.get("/notifications", headers={"Accept": "text/html"})
    assert r.status_code == 200, r.text
    assert 'href="/notifications/' in r.text

    r = client.get("/notifications/unread_count")
    assert r.json() == {"count": 1}

    r = client.get("/notifications")
    notification_id = r.json()[0]["id"]

    r = client.get(f"/notifications/{notification_id}/open", follow_redirects=False)
    assert r.status_code == 303, r.text
    assert r.headers["location"] == f"/cards/{card_id}"

    r = client.get("/notifications/unread_count")
    assert r.json() == {"count": 0}
