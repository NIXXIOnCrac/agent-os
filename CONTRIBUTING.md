# Contributing to AgentOS

Contributions are welcome once the repository is publicly available.

1. Open an issue describing the problem or proposed feature.
2. Create a branch with a focused change.
3. Run `cd backend && pytest -q` for backend changes.
4. Run `cd apps/web && npm run typecheck && npm run build` for frontend changes.
5. Submit a PR describing changes, manual verification and security implications.

Never commit credentials, private user memories or keys. Models must never be allowed to grant themselves tools or permissions. Explain breaking changes in documentation and add tests for new code.
