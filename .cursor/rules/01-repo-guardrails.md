Project guardrails

- Use clear, self-documenting names; avoid abbreviations.
- Do not reformat unrelated code in edits.
- Prefer small, focused edits; keep existing indentation and style.
- For GitHub Projects/CLI code, support both GitHub-hosted and local runs.
- Never hardcode secrets; use environment variables from `env.example`.

Branch protection

- Work happens on feature branches; merge via PR.
- Require at least 1 review and CODEOWNERS approval.
- Disallow force-push and branch deletion for protected branches.

Backend

- Python 3.11; prefer type hints and Pydantic for schemas.
- Lint with ruff; format with black; keep logs structured.

Frontend

- Use npm scripts for lint/test/build; keep CI non-interactive.


