import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.game_service import GameSession, get_session
from app.models import GameMode, GameState

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Soc Ops - Social Bingo")
app.add_middleware(SessionMiddleware, secret_key="soc-ops-secret-key")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


def _get_game_session(request: Request) -> GameSession:
    """Get or create a game session using cookie-based sessions."""
    if "session_id" not in request.session:
        request.session["session_id"] = uuid.uuid4().hex
    return get_session(request.session["session_id"])


def _render_session(request: Request, session: GameSession) -> Response:
    if session.mode == GameMode.SCAVENGER:
        template = "components/scavenger_screen.html"
    elif session.mode == GameMode.CARD_DECK:
        template = "components/card_deck_screen.html"
    else:
        template = "components/game_screen.html"
    return templates.TemplateResponse(request, template, {"session": session})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    session = _get_game_session(request)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"session": session, "GameState": GameState},
    )


@app.post("/start", response_class=HTMLResponse)
async def start_game(request: Request) -> Response:
    session = _get_game_session(request)
    session.start_game()
    return _render_session(request, session)


@app.post("/start-scavenger", response_class=HTMLResponse)
async def start_scavenger(request: Request) -> Response:
    session = _get_game_session(request)
    session.start_scavenger()
    return _render_session(request, session)


@app.post("/start-card-deck", response_class=HTMLResponse)
async def start_card_deck(request: Request) -> Response:
    session = _get_game_session(request)
    session.start_card_deck()
    return _render_session(request, session)


@app.post("/draw-card", response_class=HTMLResponse)
async def draw_card(request: Request) -> Response:
    session = _get_game_session(request)
    session.draw_card()
    return _render_session(request, session)


@app.post("/toggle/{square_id}", response_class=HTMLResponse)
async def toggle_square(request: Request, square_id: int) -> Response:
    session = _get_game_session(request)
    session.handle_square_click(square_id)
    return _render_session(request, session)


@app.post("/reset", response_class=HTMLResponse)
async def reset_game(request: Request) -> Response:
    session = _get_game_session(request)
    session.reset_game()
    return templates.TemplateResponse(
        request,
        "components/start_screen.html",
        {"session": session, "GameState": GameState},
    )


@app.post("/dismiss-modal", response_class=HTMLResponse)
async def dismiss_modal(request: Request) -> Response:
    session = _get_game_session(request)
    session.dismiss_modal()
    return _render_session(request, session)


def run() -> None:
    """Entry point for the application."""
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
