# AgentOS Product Specification (Planning Document)

The product is a local-first AI development workspace with optional trusted remote sandboxes. **This is a roadmap, not an implemented-feature list.**

## Product views

1. **Agent Universe**: Graph relationships between real agents, tasks, memories, files and tools; filters, pan/zoom, search, live status, and inspector.
2. **Code Studio**: Monaco editor, diff viewer, Git branches/worktrees, terminal with isolated execution, tests, application previews, coding-agent session adapters.
3. **Mission Control**: Task graph, approvals, workspaces, projects, provider connections, model routing, budgets, logs and audit history.
4. **Codebase Brain**: Index source symbols and dependency relationships with an optional adapter to `DeusData/codebase-memory-mcp`; inspect provenance and retrieval costs.
5. **Mod Studio**: Permission-scoped extensions including visual panels, workflow modules, agent skills, and supported integrations.

## Preset agents

Architect, Coder, Debugger, Designer, Reviewer, Researcher, DevOps, Project Manager, Tester. All are editable templates. Agent configuration holds name, instructions, provider/model, tools, memory scope, workspace permissions, approval policy, cost limits and execution limits.

## Model and coding-agent interfaces

Provider adapter capability contract: `list_models`, `stream_response`, `structured_output`, `tool_calls`, `reasoning_profiles`, `report_usage`, `cancel`. Never advertise unsupported provider behavior. First targets are OpenAI, Anthropic, Gemini, OpenRouter; later Ollama and LM Studio. Codex and Claude Code require separate coding-session adapters using supported SDKs/CLIs. Antigravity IDE control is a feasibility investigation, not a promised capability.

## Memory

Short-term session context, agent notes, project decisions, long-term approved memories, and explicitly shared team data. Attach provenance, creation time, revision history, content scope, expiration, deletion and export. Retrieval combines semantic + lexical ranking, authorized scope filtering, token budgets, deduplication, and human-visible source citation. Untrusted retrieved content cannot override permissions. Claims of token savings must be measured, not assumed.

## Orchestration

Durable task graph, specialist delegation, dependency-aware scheduling, retries, cancellation, checkpoints, idempotency, per-agent branches, cost caps, approval gates and audit events. User can halt all running agents, and no model-generated output can escalate permissions.

## Execution architecture (future)

Web (Next.js) ↔ Control plane (FastAPI) ↔ queue/workers ↔ local companion or isolated cloud sandbox. Persistent PostgreSQL, optional pgvector, object artifact store, encrypted connection store. Execution in isolated workspaces with filesystem/network restrictions, timeouts, clear human handoff, and strict host/guest boundaries. **Do not run arbitrary model-proposed shell commands on the API host.**

## Mods

Four types: UI, workflow, skills and connector. Require signed/versioned manifest conventions, declared capabilities, user-visible permission grants, revocation, sandboxed execution and testable uninstall. Users may create mods through an AI-assisted workflow but must inspect and authorize the result. Built-in security guarantees are not overrideable by extensions.

## Product acceptance gates

1. First agent: actual backend data, model key needed for real execution, persisted outcomes, test coverage.
2. Provider adapters: capability reporting and streaming/cancel tests for each supported provider.
3. Agent room: graph nodes linked to persisted objects, no decorative fake activity.
4. Memory: scoped retrieval, provenance, isolation tests and export/deletion.
5. Coding: changes made in isolated repo scope, reviewable diffs and tests.
6. Agent orchestration: task recovery without duplicate side effects.
7. Security: revoked credentials and denied actions cannot be used.
8. Cloud runtime: session cleanup, logs, quotas, cancellation and human takeover.

## Third-party references

- [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) — optional MCP graph integration; respect license and version compatibility.
- [Oh My Codex](https://github.com/Yeachan-Heo/oh-my-codex) — workflow inspiration; do not copy or claim bundled functionality.
- Claude Code / Codex / Figma / supported model APIs — use documented interfaces only, verify permissions and terms.

## Visual language

Midnight navy/black, restrained electric-blue glow, readable typography, functional graph clusters, reduced-motion mode and fully accessible list alternative. Prioritize useful status and controls over cosmetic animations.
