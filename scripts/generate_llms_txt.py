#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt from the Mintlify MDX sources.

llms.txt      - the index defined by https://llmstxt.org (H1, blockquote, H2 link lists)
llms-full.txt - every page's full content flattened into one plain-markdown file

Run from the docs repo root:  python scripts/generate_llms_txt.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = os.environ.get("DOCS_BASE_URL", "https://docs.avaliar.ai").rstrip("/")

# Components that become a heading, keyed to the attribute holding their label.
HEADING_TAGS = {"Step", "Tab", "Accordion"}
# Components that become a blockquote callout.
CALLOUT_TAGS = {"Note": "Note", "Tip": "Tip", "Info": "Info",
                "Warning": "Warning", "Check": "Check", "Danger": "Warning"}
# Layout-only wrappers that are simply dropped.
WRAPPER_TAGS = {"CardGroup", "Steps", "Tabs", "AccordionGroup", "CodeGroup",
                "Columns", "Frame", "Update", "Expandable"}

ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
# Quote-aware so attribute values may themselves contain ">".
OPEN_RE = re.compile(r'^\s*<([A-Z]\w*)\b((?:[^>"]|"[^"]*")*)>\s*$')
CLOSE_RE = re.compile(r"^\s*</([A-Z]\w*)>\s*$")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
REL_LINK_RE = re.compile(r"\]\((/[^)\s]*)\)")


def attrs(raw: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(raw))


def abs_url(href: str, page_url: str) -> str:
    if href.startswith("#"):
        return page_url + href
    if href.startswith("/"):
        return SITE + href
    return href


def clean_inline(text: str, page_url: str) -> str:
    text = re.sub(r"</?Badge>", "", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    return REL_LINK_RE.sub(lambda m: "](" + SITE + m.group(1) + ")", text)


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    block, body = raw[3:end], raw[end + 4:]
    meta = {}
    for line in block.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body.lstrip("\n")


def convert(body: str, page_url: str) -> str:
    """Flatten Mintlify MDX components into portable markdown.

    Every component opens a scope with its own buffer. Raw source lines written
    into a scope are dedented by that scope's own indentation, so the nesting
    Mintlify uses for readability does not survive as markdown indented-code
    blocks. Content handed up from a closed child scope is already formatted and
    is passed through untouched.
    """
    lines = body.splitlines()
    page: list[str] = []
    stack: list[dict] = []
    base_level = 1              # level of the most recent real markdown heading
    step_counts: list[int] = [] # one counter per open <Steps> block
    fence: str | None = None

    def new_scope(tag: str, **extra) -> dict:
        scope = {"tag": tag, "buffer": [], "indent": None}
        scope.update(extra)
        return scope

    def sink() -> list[str]:
        return stack[-1]["buffer"] if stack else page

    def emit_block(block: list[str]) -> None:
        """Append already-formatted lines verbatim."""
        sink().extend(block)

    def emit_source(line: str) -> None:
        """Append a raw source line, dedented to its scope."""
        if stack:
            scope = stack[-1]
            if scope["indent"] is None and line.strip():
                scope["indent"] = len(line) - len(line.lstrip(" "))
            if scope["indent"]:
                strip = min(scope["indent"], len(line) - len(line.lstrip(" ")))
                line = line[strip:]
        sink().append(line.rstrip())

    def heading_level() -> int:
        depth = sum(1 for f in stack if f.get("heading"))
        return min(base_level + depth + 1, 6)

    def trimmed(block: list[str]) -> list[str]:
        block = [l.rstrip() for l in block]
        while block and not block[0].strip():
            block.pop(0)
        while block and not block[-1].strip():
            block.pop()
        return block

    for raw_line in lines:
        fence_match = FENCE_RE.match(raw_line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker[:3]
            elif marker.startswith(fence):
                fence = None
            emit_source(raw_line)
            continue
        if fence is not None:
            emit_source(raw_line)
            continue

        open_match = OPEN_RE.match(raw_line)
        if open_match:
            tag, props = open_match.group(1), attrs(open_match.group(2))

            if tag == "Steps":
                step_counts.append(0)
                stack.append(new_scope(tag))
                continue
            if tag in WRAPPER_TAGS:
                stack.append(new_scope(tag))
                continue
            if tag in HEADING_TAGS:
                title = clean_inline(props.get("title", tag), page_url)
                if tag == "Step" and step_counts:
                    step_counts[-1] += 1
                    title = f"Step {step_counts[-1]}: {title}"
                stack.append(new_scope(tag, heading=True,
                                       label=f"{'#' * heading_level()} {title}"))
                continue
            if tag in CALLOUT_TAGS:
                stack.append(new_scope(tag, label=CALLOUT_TAGS[tag]))
                continue
            if tag == "Card":
                stack.append(new_scope(tag, props=props))
                continue

            stack.append(new_scope(tag))  # unknown component: keep its contents
            continue

        close_match = CLOSE_RE.match(raw_line)
        if close_match:
            tag = close_match.group(1)
            if tag == "Steps" and step_counts:
                step_counts.pop()
            if not stack or stack[-1]["tag"] != tag:
                continue

            scope = stack.pop()
            content = trimmed(scope["buffer"])

            if tag in WRAPPER_TAGS:
                emit_block(content)
                continue

            if scope.get("heading"):
                emit_block(["", scope["label"], ""] + content + [""])
                continue

            if tag in CALLOUT_TAGS:
                if content:
                    quoted = [f"> **{scope['label']}:** {content[0].strip()}"]
                    quoted += [f"> {l.strip()}" if l.strip() else ">" for l in content[1:]]
                    emit_block([""] + quoted + [""])
                continue

            if tag == "Card":
                title = clean_inline(scope["props"].get("title", ""), page_url)
                href = scope["props"].get("href", "")
                label = f"[{title}]({abs_url(href, page_url)})" if href else f"**{title}**"
                if any(FENCE_RE.match(l) or l.lstrip().startswith("|") for l in content):
                    emit_block([""] + [f"**{title}**" +
                                       (f" ({abs_url(href, page_url)})" if href else "")]
                               + [""] + content + [""])
                else:
                    summary = re.sub(r"\s+", " ",
                                     " ".join(l.strip() for l in content if l.strip())).strip()
                    emit_block([f"- {label}" + (f": {summary}" if summary else "")])
                continue

            emit_block(content)
            continue

        heading_match = HEADING_RE.match(raw_line)
        if heading_match and not stack:
            base_level = len(heading_match.group(1))

        emit_source(clean_inline(raw_line, page_url))

    text = "\n".join(page)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


OPTIONAL_PAGES = {"sdk/contributing"}


def load_pages() -> list[tuple[str, list[str]]]:
    """Return [(group name, [page slug, ...]), ...] in docs.json navigation order."""
    config = json.loads((ROOT / "docs.json").read_text())
    groups = []
    for tab in config["navigation"]["tabs"]:
        for group in tab.get("groups", []):
            groups.append((group["group"], list(group["pages"])))
    return groups


def main() -> int:
    groups = load_pages()
    pages: dict[str, dict] = {}

    for _, slugs in groups:
        for slug in slugs:
            path = ROOT / f"{slug}.mdx"
            if not path.exists():
                print(f"warning: {slug}.mdx not found, skipping", file=sys.stderr)
                continue
            meta, body = parse_frontmatter(path.read_text())
            url = f"{SITE}/{slug}"
            pages[slug] = {
                "title": meta.get("title", slug),
                "description": meta.get("description", ""),
                "url": url,
                "content": convert(body, url),
            }

    intro = (ROOT / "scripts" / "llms_intro.md").read_text().rstrip()

    # ---- llms.txt -------------------------------------------------------
    index = [intro, ""]
    for group, slugs in groups:
        index.append(f"## {group}")
        index.append("")
        for slug in slugs:
            page = pages.get(slug)
            if not page:
                continue
            if slug in OPTIONAL_PAGES:
                continue
            desc = page["description"]
            index.append(f"- [{page['title']}]({page['url']}.md)" + (f": {desc}" if desc else ""))
        index.append("")
    index += [
        "## Optional",
        "",
        "- [Contributing to the SDK](https://docs.avaliar.ai/sdk/contributing.md): "
        "Local development setup, project layout, and release process for the Python SDK.",
        "- [Avaliar Dashboard](https://app.avaliar.ai): "
        "The web application where traces, issues, alerts, and reports live.",
        "- [Python SDK on PyPI](https://pypi.org/project/avaliar-python-sdk/): "
        "Package releases and version history.",
        "- [GitHub organization](https://github.com/avaliar-ai): Source repositories.",
        "",
    ]
    (ROOT / "llms.txt").write_text("\n".join(index))

    # ---- llms-full.txt --------------------------------------------------
    full = [intro, ""]
    for group, slugs in groups:
        for slug in slugs:
            page = pages.get(slug)
            if not page:
                continue
            full.append("---")
            full.append("")
            full.append(f"# {page['title']}")
            full.append("")
            if page["description"]:
                full.append(f"> {page['description']}")
                full.append("")
            full.append(f"Source: {page['url']}  |  Section: {group}")
            full.append("")
            full.append(page["content"])
            full.append("")
    (ROOT / "llms-full.txt").write_text("\n".join(full).rstrip() + "\n")

    print(f"llms.txt       {len((ROOT / 'llms.txt').read_bytes()):>8,} bytes")
    print(f"llms-full.txt  {len((ROOT / 'llms-full.txt').read_bytes()):>8,} bytes  "
          f"({len(pages)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
