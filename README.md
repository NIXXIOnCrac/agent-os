# AgentOS

**A local-first, open-source AI agent workspace.** Build agents, see how they relate, assign missions, and inspect persistent memory from one dark, graph-based interface.

> **Status: v0.1 development starter — not production ready.** This repository includes a working local API and a connected Agent Universe UI. It does **not yet** provide an IDE, tool-running agents, sandboxed terminals, Codex/Claude Code sessions, multi-provider connection UI, or production security. Those are documented future milestones.

## Implemented today

- Nine built-in specialist agent definitions and a custom-agent creator.
- An interactive constellation-style **Agent Universe** driven by backend data.
- Queue, cancel (before execution), run, and inspect local agent tasks.
- OpenAI-compatible chat-completions adapter, configurable from **server-side** environment variables. No fake model replies if a key is missing.
- Persistent project and agent memory notes in local SQLite, with visible delete control.
- Task event timeline stored in the database and exposed by API.
- Local health and capability endpoints.
- Python API contract tests with a fake provider used **only in tests**.
- GitHub Actions CI for backend tests and frontend type-check/build.

## Quick start (Windows PowerShell)

Requires **Python 3.12+** and **Node.js 22+**. Two terminals are required.

### 1. Backend (terminal one)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
# Backend API works without model keys; agent execution requires them.
$env:OPENAI_API_KEY = "YOUR_KEY"   # optional — do not commit
$env:AGENTOS_MODEL = "YOUR_MODEL_ID" # optional
python -m uvicorn agentos.main:app --host 127.0.0.1 --port 8000
```

Visit http://127.0.0.1:8000/docs for interactive API documentation. On macOS/Linux, use `source .venv/bin/activate` and `export` instead of PowerShell `$env:`.

### 2. Web app (terminal two)

```powershell
cd apps/web
npm install
npm run dev
```

Visit **http://127.0.0.1:3000**. The frontend communicates with the local API at `http://127.0.0.1:8000` by default.

### 3. Use AgentOS

1. Click a specialist agent node in the Universe.
2. Assign a mission, then click its **play** control if a model is configured.
3. Open **Missions** to inspect task results.
4. Open **Memory** to add or delete project notes.
5. Create a custom agent using **Create custom agent**.

**Important:** In v0.1, a mission sends a text request to a model; it does **not** execute shell commands, edit files, or control your computer. The status and response represent real persisted API requests, not a simulated tool run.

## Tests

```bash
cd backend
python -m pip install -e '.[dev]'
pytest -q
```

Frontend, after `npm install`:

```bash
cd apps/web
npm run typecheck
npm run build
```

## Architecture

```text
Next.js Agent Universe (React/TypeScript)
          |
   REST API (FastAPI)  -- OpenAI-compatible model endpoint (opt-in)
          |
SQLite local database (agent definitions, tasks, events, memories)
```

The v0.1 adapter uses OpenAI-compatible `/chat/completions`. Some reasoning-first models do not support this endpoint or standard parameters; inspect capabilities before enabling them. The planned v1 architecture will add provider-specific adapters, event streaming, PostgreSQL, permission services, runtime workers, and isolated execution environments.

See [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md) for the complete build specification and [docs/ROADMAP.md](docs/ROADMAP.md) for milestones.

## Security notice

**Never expose this prototype API publicly.** It currently has no account authentication or project/tenant isolation. Always start the API bound to `127.0.0.1`. Only use trusted local data. Configure model keys in your shell or secure secret manager; never in the browser, public GitHub repository, or committed `.env` files. **Do not deploy v0.1 to public hosting.**

Future versions require server-side access control, credential encryption, workspace isolation, per-action approvals, logs with redaction, sandboxing, and verified providers before production use.

## Repository guide

- `apps/web` — browser user interface.
- `backend/agentos` — local API, SQLite persistence, and model adapter.
- `backend/tests` — automated API tests.
- `docs` — architecture, planned features, and milestones.
- `.github/workflows` — GitHub Actions.

## Planned features

**Agent Universe · Code Studio · Mission Control · Codebase Brain · Mod Studio**; configurable reasoning levels; model providers (OpenAI, Anthropic, Gemini, OpenRouter, Ollama, LM Studio); Codex and Claude Code integrations; investigated Antigravity support; scoped memory, budgets, approvals, orchestration, terminal, Figma, and cloud runtimes. None of those unimplemented integrations should be presented as active.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Start with tests or a focused issue; avoid PRs that silently widen tool permissions. Contributors must not add real credentials to the repository.

## License

MIT, see [LICENSE](LICENSE). Code from third-party projects must follow its own license and attribution requirements.
