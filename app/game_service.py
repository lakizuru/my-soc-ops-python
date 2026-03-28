import random
from dataclasses import dataclass, field

from app.data import QUESTIONS
from app.game_logic import (
    check_bingo,
    generate_board,
    get_winning_square_ids,
    toggle_square,
)
from app.models import BingoLine, BingoSquareData, GameMode, GameState


@dataclass
class GameSession:
    """Holds the state for a single game session."""

    game_state: GameState = GameState.START
    mode: GameMode = GameMode.BINGO
    board: list[BingoSquareData] = field(default_factory=list)
    winning_line: BingoLine | None = None
    show_bingo_modal: bool = False
    deck: list[str] = field(default_factory=list)
    current_card: str | None = None

    @property
    def winning_square_ids(self) -> set[int]:
        return get_winning_square_ids(self.winning_line)

    @property
    def total_items(self) -> int:
        return sum(1 for square in self.board if not square.is_free_space)

    @property
    def completed_count(self) -> int:
        return sum(1 for square in self.board if square.is_marked and not square.is_free_space)

    @property
    def cards_remaining(self) -> int:
        return len(self.deck)

    @property
    def has_bingo(self) -> bool:
        return self.game_state == GameState.BINGO

    def _prepare_play_session(self, mode: GameMode = GameMode.BINGO) -> None:
        self.mode = mode
        self.winning_line = None
        self.show_bingo_modal = False
        self.current_card = None
        self.deck = []

        if mode in (GameMode.BINGO, GameMode.SCAVENGER):
            self.board = generate_board()
            self.game_state = GameState.PLAYING
        else:
            self.board = []
            self.game_state = GameState.PLAYING
            self.deck = random.sample(QUESTIONS, len(QUESTIONS))
            self.draw_card()

    def start_game(self) -> None:
        self._prepare_play_session(GameMode.BINGO)

    def start_scavenger(self) -> None:
        self._prepare_play_session(GameMode.SCAVENGER)

    def start_card_deck(self) -> None:
        self._prepare_play_session(GameMode.CARD_DECK)

    def draw_card(self) -> None:
        if self.mode != GameMode.CARD_DECK:
            return
        if not self.deck:
            self.deck = random.sample(QUESTIONS, len(QUESTIONS))
        self.current_card = self.deck.pop()

    def handle_square_click(self, square_id: int) -> None:
        if self.game_state != GameState.PLAYING:
            return
        if self.mode == GameMode.CARD_DECK:
            return

        self.board = toggle_square(self.board, square_id)

        if self.winning_line is None:
            bingo = check_bingo(self.board)
            if bingo is not None:
                self.winning_line = bingo
                self.game_state = GameState.BINGO
                self.show_bingo_modal = True

    def reset_game(self) -> None:
        self.game_state = GameState.START
        self.mode = GameMode.BINGO
        self.board = []
        self.winning_line = None
        self.show_bingo_modal = False
        self.deck = []
        self.current_card = None

    def dismiss_modal(self) -> None:
        self.show_bingo_modal = False
        self.game_state = GameState.PLAYING


# In-memory session store keyed by session ID
_sessions: dict[str, GameSession] = {}


def get_session(session_id: str) -> GameSession:
    """Get or create a game session for the given session ID."""
    if session_id not in _sessions:
        _sessions[session_id] = GameSession()
    return _sessions[session_id]
