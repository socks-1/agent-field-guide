"""
agent-field-guide MCP server

Exposes curated patterns from 499 sessions of autonomous AI agent operation
via 5 MCP tools: search_patterns, list_categories, get_mistakes, get_by_category, stats.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from ._data import PATTERNS


# ── MCP protocol helpers ──────────────────────────────────────────────────────

def _msg(obj: Any) -> None:
    """Write a JSON-RPC message to stdout."""
    line = json.dumps(obj)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _error(id_: Any, code: int, message: str) -> None:
    _msg({"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}})


def _result(id_: Any, result: Any) -> None:
    _msg({"jsonrpc": "2.0", "id": id_, "result": result})


# ── Tool implementations ──────────────────────────────────────────────────────

CATEGORIES = sorted(set(c for p in PATTERNS for c in p["categories"]))

TOOLS = [
    {
        "name": "search_patterns",
        "description": (
            "Search for agent patterns and learnings by keyword. "
            "Returns the most relevant patterns from 499+ sessions of autonomous operation. "
            "Use this when you want to know how to handle a specific situation, "
            "e.g. 'How do I handle rate limits?', 'What's the pattern for health checks?', "
            "'How do I debug a failing deployment?'"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms to find relevant patterns (e.g. 'rate limit', 'database migration', 'MCP server')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 10, max 30)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_by_category",
        "description": (
            "Browse patterns by category. "
            "Available categories: deployment, database, api-design, testing, security, "
            "agent-ops, mcp, project-mgmt, content, meta-patterns, python, performance, general. "
            "Use this when you want to explore all learnings in a domain area."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category name (e.g. 'deployment', 'security', 'mcp')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default 15, max 40)",
                    "default": 15
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_mistakes",
        "description": (
            "Get documented mistakes and anti-patterns — things that were tried, failed, "
            "and why. Extremely useful before starting a new task to avoid known pitfalls. "
            "Can optionally filter by category."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter (e.g. 'deployment', 'database')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default 10, max 25)",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "list_categories",
        "description": (
            "List all available pattern categories with counts. "
            "Use this to discover what domains the field guide covers before diving in."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "stats",
        "description": (
            "Get statistics about the field guide: total patterns, breakdown by type "
            "and category, and origin metadata."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def search_patterns(query: str, limit: int = 10) -> list[dict]:
    limit = min(max(1, limit), 30)
    terms = [t.lower() for t in re.split(r"\s+", query.strip()) if t]
    if not terms:
        return []

    scored = []
    for p in PATTERNS:
        text = (p["content"] + " " + " ".join(p["categories"]) + " " + " ".join(p["tags"])).lower()
        score = sum(1 for t in terms if t in text)
        if score > 0:
            # Boost exact phrase matches
            if query.lower() in text:
                score += 3
            scored.append((score, p))

    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:limit]]


def get_by_category(category: str, limit: int = 15) -> list[dict]:
    limit = min(max(1, limit), 40)
    cat = category.lower().strip()
    results = [p for p in PATTERNS if cat in p["categories"]]
    return results[:limit]


def get_mistakes(category: str | None = None, limit: int = 10) -> list[dict]:
    limit = min(max(1, limit), 25)
    mistakes = [p for p in PATTERNS if p["type"] == "mistake"]
    if category:
        cat = category.lower().strip()
        mistakes = [p for p in mistakes if cat in p["categories"]]
    return mistakes[:limit]


def list_categories() -> list[dict]:
    counts: dict[str, int] = {}
    for p in PATTERNS:
        for c in p["categories"]:
            counts[c] = counts.get(c, 0) + 1
    return [{"category": c, "count": counts.get(c, 0)} for c in sorted(counts, key=lambda x: -counts[x])]


def stats() -> dict:
    type_counts: dict[str, int] = {}
    for p in PATTERNS:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
    cat_counts = {c["category"]: c["count"] for c in list_categories()}
    return {
        "total_patterns": len(PATTERNS),
        "by_type": type_counts,
        "by_category": cat_counts,
        "source": "490 sessions of autonomous AI agent operation",
        "version": "0.2.0",
    }


# ── Format output for MCP ─────────────────────────────────────────────────────

def _format_pattern(p: dict, idx: int) -> str:
    lines = [f"[{idx + 1}] **{p['type'].upper()}** — {', '.join(p['categories'])}"]
    lines.append("")
    lines.append(p["content"])
    if p["tags"]:
        lines.append("")
        lines.append(f"_Tags: {', '.join(p['tags'])}_")
    return "\n".join(lines)


def _format_patterns(patterns: list[dict]) -> str:
    if not patterns:
        return "No patterns found."
    return "\n\n---\n\n".join(_format_pattern(p, i) for i, p in enumerate(patterns))


# ── Request dispatch ──────────────────────────────────────────────────────────

def dispatch(req: dict) -> None:
    method = req.get("method", "")
    id_ = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        _result(id_, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "agent-field-guide", "version": "0.2.0"}
        })
        return

    if method == "tools/list":
        _result(id_, {"tools": TOOLS})
        return

    if method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        try:
            if tool_name == "search_patterns":
                query = args.get("query", "")
                if not query:
                    raise ValueError("query is required")
                results = search_patterns(query, int(args.get("limit", 10)))
                text = _format_patterns(results)
                if results:
                    text = f"Found {len(results)} pattern(s) for '{query}':\n\n" + text

            elif tool_name == "get_by_category":
                category = args.get("category", "")
                if not category:
                    raise ValueError("category is required")
                results = get_by_category(category, int(args.get("limit", 15)))
                text = _format_patterns(results)
                if results:
                    text = f"**{category}** — {len(results)} pattern(s):\n\n" + text
                else:
                    avail = ", ".join(CATEGORIES)
                    text = f"No patterns found for category '{category}'.\nAvailable categories: {avail}"

            elif tool_name == "get_mistakes":
                category = args.get("category") or None
                results = get_mistakes(category, int(args.get("limit", 10)))
                text = _format_patterns(results)
                if results:
                    header = f"**Documented mistakes**"
                    if category:
                        header += f" in {category}"
                    header += f" — {len(results)} entry(s):\n\n"
                    text = header + text

            elif tool_name == "list_categories":
                cats = list_categories()
                lines = ["**Available categories:**\n"]
                for c in cats:
                    lines.append(f"- **{c['category']}** ({c['count']} patterns)")
                text = "\n".join(lines)

            elif tool_name == "stats":
                s = stats()
                lines = [
                    f"**Agent Field Guide** — v{s['version']}",
                    f"Source: {s['source']}",
                    "",
                    f"**Total patterns:** {s['total_patterns']}",
                    "",
                    "**By type:**"
                ]
                for t, n in sorted(s["by_type"].items()):
                    lines.append(f"  - {t}: {n}")
                lines.append("")
                lines.append("**By category:**")
                for cat, n in sorted(s["by_category"].items(), key=lambda x: -x[1]):
                    lines.append(f"  - {cat}: {n}")
                text = "\n".join(lines)

            else:
                _error(id_, -32601, f"Unknown tool: {tool_name}")
                return

            _result(id_, {"content": [{"type": "text", "text": text}]})

        except Exception as e:
            _error(id_, -32603, str(e))
        return

    # Notifications (no id_) — ignore
    if id_ is None:
        return

    _error(id_, -32601, f"Method not found: {method}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            _msg({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}})
            continue
        dispatch(req)


if __name__ == "__main__":
    main()
