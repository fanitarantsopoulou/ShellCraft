"""Markdown -> HTML. Raw HTML in content is escaped, never passed through."""

from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table")


def render_block(text: str) -> str:
    return _md.render(text)


def render_inline(text: str) -> str:
    return _md.renderInline(text)
