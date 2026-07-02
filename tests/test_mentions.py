from app.mentions import extract_mentions


def test_single_mention():
    assert extract_mentions("hey @alice, can you look at this?") == ["alice"]


def test_multiple_mentions_in_order():
    assert extract_mentions("cc @alice and @bob please") == ["alice", "bob"]


def test_duplicate_mention_deduped():
    assert extract_mentions("@alice ping @bob then @alice again") == ["alice", "bob"]


def test_no_mentions_returns_empty_list():
    assert extract_mentions("no mentions in this body at all") == []


def test_email_address_is_not_a_mention():
    assert extract_mentions("contact me at foo@bar.com for details") == []
