import os

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.mentions import linkify_mentions

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["linkify_mentions"] = linkify_mentions


def wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "")
