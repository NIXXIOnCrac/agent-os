# AgentOS Roadmap

## v0.1 — Local foundation (IN PROGRESS)
- [x] Repo scaffold, architecture docs, MIT license and CI workflow.
- [x] Local-only FastAPI API, agent presets/custom agents, task data model.
- [x] SQLite memory notes, task history, real model adapter.
- [x] Graph-based Agent Universe frontend.
- [x] Backend API tests.
- [ ] Confirm GitHub Actions success after publishing.
- [ ] Confirm frontend build in a network-enabled environment.
- [ ] Add workspace security and per-user authentication before any public deployment.

## v0.2 — Secure control plane
- [ ] PostgreSQL schema, migrations and multi-tenant isolation.
- [ ] Authentication, server-side RBAC and encrypted provider connections.
- [ ] SSE/WebSocket event transport, true cancellation and background workers.
- [ ] Provider-specific Anthropic, Gemini and OpenRouter adapters.
- [ ] Capability-based reasoning controls and budget accounting.

## v0.3 — Graph intelligence and orchestrator
- [ ] Integrate codebase-memory-mcp with permission boundaries.
- [ ] Project graph, search, zoom/pan, dependency tracing and code references.
- [ ] Structured memory retrieval and provenance.
- [ ] Specialist delegation, approval gates, durable tasks, checkpoints.

## v0.4 — Developer Studio
- [ ] Monaco editor, file explorer, Git worktrees and diffs.
- [ ] Local companion, terminal restrictions, tests and previews.
- [ ] Codex and Claude Code adapters where supported.
- [ ] Ollama and LM Studio model endpoints.

## v0.5 — Design and mods
- [ ] Figma workflows and visual regression previews.
- [ ] Mod manifest/permissions, visual mods and local extension manager.
- [ ] Replay, file history, cost dashboard, blast radius and session rescue.

## v0.6+ — Cloud and public release
- [ ] Isolated cloud runtimes, browser control and human takeover.
- [ ] Verified Antigravity interoperability or documented limitation.
- [ ] Hardening, threat modeling, accessibility, performance and packaging.

No feature is considered complete until it has tests and a reproducible real-world demonstration.
