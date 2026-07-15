"""Safe Markdown → HTML for module summaries."""

from __future__ import annotations

import bleach
from markdown_it import MarkdownIt
from markupsafe import Markup

_MD = MarkdownIt("commonmark", {"breaks": True, "linkify": False}).disable("image")

_ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "a",
    "code",
    "pre",
    "blockquote",
]
_ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
}
_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def render_markdown(text: str) -> Markup:
    """Convert Markdown to sanitized HTML Markup safe for Jinja."""
    if not text or not text.strip():
        return Markup("")
    raw_html = _MD.render(text)
    cleaned = bleach.clean(
        raw_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    )
    # Force safe link behavior for localhost app
    cleaned = bleach.linkify(
        cleaned,
        parse_email=False,
        callbacks=[_force_rel_noopener],
        skip_tags=["pre", "code"],
    )
    return Markup(cleaned)


def _force_rel_noopener(attrs: dict, new: bool = False) -> dict:  # noqa: FBT001, FBT002
    href = attrs.get((None, "href"), "")
    if href.startswith(("http://", "https://", "mailto:")):
        attrs[(None, "rel")] = "noopener noreferrer"
        attrs[(None, "target")] = "_blank"
    return attrs
