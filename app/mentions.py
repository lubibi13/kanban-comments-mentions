import re

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
