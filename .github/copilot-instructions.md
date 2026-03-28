# Copilot Workspace Instructions

## Required checklist

- [ ] `uv sync`
- [ ] `uv run ruff check .`
- [ ] `uv run pytest`

## What this app is

Server-rendered FastAPI + Jinja2 + HTMX Social Bingo. Game state lives in `app/game_service.py`; sessions are kept in-memory in `_sessions` and keyed by `session_id`.

## Key files

- `app/main.py`: routes, session creation, HTMX endpoints
- `app/game_service.py`: `GameSession`, game flow, modal state
- `app/game_logic.py`: board generation, toggle logic, bingo detection
- `app/templates/`: Jinja fragments, especially `components/game_screen.html` and `components/start_screen.html`
- `tests/test_api.py`: endpoint and HTMX response validation

## Design guide

- Use dark, Stranger Things-inspired styling through CSS only; avoid changing backend request flow.
- Keep HTMX attributes intact: `hx-post`, `hx-target="#game-container"`, `hx-swap="outerHTML"`.
- Favor retro neon red accents, black backgrounds, and glowing text shadows in `app/static/css/app.css`.
- Update templates by changing classes and structure in `app/templates/components/*`, not by adding client-side JS.

## Agent notes

- Never use Simple Browser. Run the app and verify with a browser or HTTP request.
- Keep logic server-side; this app intentionally avoids client-side application state.
- If `uv` is unavailable, use `python -m uv` for sync/test/run commands.
