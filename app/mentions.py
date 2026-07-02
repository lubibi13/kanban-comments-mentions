import re

from markupsafe import Markup, escape
from sqlmodel import Session, select

from app.models import User

_MENTION_RE = re.compile(r"(?:^|(?<=\s))@(\w+)")


def extract_mentions(body: str) -> list[str]:
    seen: set[str] = set()
    mentions: list[str] = []
    for match in _MENTION_RE.finditer(body):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            mentions.append(name)
    return mentions


def find_mentioned_users(body: str, session: Session) -> list[User]:
    usernames = extract_mentions(body)
    if not usernames:
        return []
    return session.exec(select(User).where(User.username.in_(usernames))).all()


def linkify_mentions(body: str) -> Markup:
    pieces = []
    last_end = 0
    for match in _MENTION_RE.finditer(body):
        pieces.append(escape(body[last_end:match.start()]))
        username = match.group(1)
        pieces.append(Markup(f'<a href="/users/{username}">@{username}</a>'))
        last_end = match.end()
    pieces.append(escape(body[last_end:]))
    return Markup("").join(pieces)
