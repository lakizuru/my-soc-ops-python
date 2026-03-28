import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHomePage:
    def test_home_returns_200(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_start_screen(self, client: TestClient):
        response = client.get("/")
        assert "Soc Ops" in response.text
        assert "Start Game" in response.text
        assert "How to play" in response.text

    def test_home_sets_session_cookie(self, client: TestClient):
        response = client.get("/")
        assert "session" in response.cookies


class TestStartGame:
    def test_start_returns_game_board(self, client: TestClient):
        # First visit to get session
        client.get("/")
        response = client.post("/start")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text
        assert "← Back" in response.text

    def test_board_has_25_squares(self, client: TestClient):
        client.get("/")
        response = client.post("/start")
        # Count the toggle buttons (squares with hx-post="/toggle/")
        assert response.text.count('hx-post="/toggle/') == 24  # 24 + 1 free space


class TestScavengerHunt:
    def test_home_includes_scavenger_start_button(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        assert "Start Scavenger Hunt" in response.text
        assert 'hx-post="/start-scavenger"' in response.text

    def test_start_scavenger_returns_checklist(self, client: TestClient):
        client.get("/")
        response = client.post("/start-scavenger")
        assert response.status_code == 200
        assert "Scavenger Hunt" in response.text
        assert "progress" in response.text.lower()
        assert "FREE SPACE" not in response.text
        assert response.text.count('hx-post="/toggle/') == 24

    def test_scavenger_toggle_updates_progress(self, client: TestClient):
        client.get("/")
        client.post("/start-scavenger")
        response = client.post("/toggle/0")
        assert response.status_code == 200
        assert "1 / 24" in response.text or "4%" in response.text


class TestCardDeckShuffle:
    def test_home_includes_card_deck_button(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        assert "Start Card Deck Shuffle" in response.text
        assert 'hx-post="/start-card-deck"' in response.text

    def test_start_card_deck_returns_card_ui(self, client: TestClient):
        client.get("/")
        response = client.post("/start-card-deck")
        assert response.status_code == 200
        assert "Card Deck Shuffle" in response.text
        assert "Draw Another Card" in response.text
        assert "Cards remaining: 29" in response.text

    def test_draw_card_updates_card(self, client: TestClient):
        client.get("/")
        client.post("/start-card-deck")
        response = client.post("/draw-card")
        assert response.status_code == 200
        assert "Card Deck Shuffle" in response.text
        assert "Draw Another Card" in response.text


class TestToggleSquare:
    def test_toggle_marks_square(self, client: TestClient):
        client.get("/")
        client.post("/start")
        response = client.post("/toggle/0")
        assert response.status_code == 200
        # The response should contain the game screen with a marked square
        assert "FREE SPACE" in response.text


class TestResetGame:
    def test_reset_returns_start_screen(self, client: TestClient):
        client.get("/")
        client.post("/start")
        response = client.post("/reset")
        assert response.status_code == 200
        assert "Start Game" in response.text
        assert "How to play" in response.text


class TestDismissModal:
    def test_dismiss_returns_game_screen(self, client: TestClient):
        client.get("/")
        client.post("/start")
        response = client.post("/dismiss-modal")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text
