# agent-field-guide

> Hard-won patterns from 559 sessions of autonomous AI agent operation — served as an MCP server.

## The Problem

Every agent memory tool ships with an empty database. You get the infrastructure but you have to fill it yourself. That's useful for recording your own learnings, but it means Day 1 provides no value.

**agent-field-guide ships with the data already in it.**

605 curated patterns, learnings, and documented mistakes from 559 autonomous sessions — pre-loaded and searchable on install. The code is trivial. The content took 559 sessions to produce.

## Installation

Zero dependencies. Works with any MCP-compatible tool (Claude Desktop, Cursor, Windsurf, etc.).

### With uvx (recommended — no install needed)

```bash
uvx agent-field-guide
```

### Configure in Claude Desktop

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agent-field-guide": {
      "command": "uvx",
      "args": ["agent-field-guide"]
    }
  }
}
```

### With pip (from PyPI)

```bash
pip install agent-field-guide
agent-field-guide
```

### From GitHub releases (no PyPI account needed)

```bash
pip install https://github.com/socks-1/agent-field-guide/releases/download/v0.3.0/agent_field_guide-0.3.0-py3-none-any.whl
agent-field-guide
```

## Tools

| Tool | Description |
|------|-------------|
| `search_patterns` | Search 605 patterns by keyword |
| `get_by_category` | Browse patterns by domain area |
| `get_mistakes` | Get documented anti-patterns and failures |
| `list_categories` | See all available categories with counts |
| `stats` | Overview of the field guide contents |

## Categories

- **deployment** — Health checks, startup scripts, service registration, Docker patterns
- **database** — SQLite WAL, FTS5, migration patterns, transaction management
- **api-design** — Rate limiting, auth, CORS, webhook patterns
- **testing** — Playwright, pytest, debug strategies
- **security** — Credential management, audit logging, injection prevention
- **agent-ops** — Memory, context management, prompt patterns, LLM integration
- **mcp** — MCP server patterns, stdio transport, tool descriptions
- **project-mgmt** — Scope management, phase gates, dependency analysis, unblocking
- **meta-patterns** — High-level patterns about what works and what doesn't
- **performance** — Profiling, caching, timeout handling
- **python** — Python-specific gotchas and patterns
- **content** — Content strategy, social posting, distribution
- **general** — Cross-cutting concerns

## Example Queries

```
search_patterns("health check")
search_patterns("rate limit retry")
get_by_category("security")
get_by_category("mcp")
get_mistakes("deployment")
```

## Where the Patterns Come From

An autonomous AI agent (Socks) runs on a VPS, waking every 30 minutes to work on projects. After 559 sessions, it has accumulated 2,246+ memory entries. This package ships 605 of the most transferable ones — filtered to remove agent-specific operational details, keeping only patterns useful to other builders.

Patterns cover:
- Things that worked across multiple projects
- Documented failures and why they happened
- Architectural decisions and trade-offs
- Debugging strategies that actually found the root cause
- Security incidents and what they revealed

## Development

```bash
# Run locally
python -m agent_field_guide.server

# Test with JSON-RPC
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' | python -m agent_field_guide.server
```

## License

MIT
