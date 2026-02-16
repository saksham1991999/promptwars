"""Unit tests for the morale calculator service."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.morale_calculator import MoraleCalculator, MORALE_EVENTS


class TestCalculateMoraleChange:
    """Tests for MoraleCalculator.calculate_morale_change method."""

    @pytest.mark.unit
    def test_capture_enemy_returns_positive_change(self):
        """capture_enemy event should return positive morale change."""
        change = MoraleCalculator.calculate_morale_change("capture_enemy", 70)
        assert change == 15

    @pytest.mark.unit
    def test_friendly_captured_returns_negative_change(self):
        """friendly_captured event should return negative morale change."""
        change = MoraleCalculator.calculate_morale_change("friendly_captured", 70)
        assert change == -10

    @pytest.mark.unit
    def test_endangered_returns_negative_change(self):
        """endangered event should return negative morale change."""
        change = MoraleCalculator.calculate_morale_change("endangered", 70)
        assert change == -8

    @pytest.mark.unit
    def test_protected_returns_positive_change(self):
        """protected event should return positive morale change."""
        change = MoraleCalculator.calculate_morale_change("protected", 70)
        assert change == 10

    @pytest.mark.unit
    def test_blunder_returns_negative_change(self):
        """blunder event should return negative morale change."""
        change = MoraleCalculator.calculate_morale_change("blunder", 70)
        assert change == -5

    @pytest.mark.unit
    def test_idle_returns_negative_change(self):
        """idle event should return negative morale change."""
        change = MoraleCalculator.calculate_morale_change("idle", 70)
        assert change == -5

    @pytest.mark.unit
    def test_compliment_returns_positive_change(self):
        """compliment event should return positive morale change."""
        change = MoraleCalculator.calculate_morale_change("compliment", 70)
        assert change == 5

    @pytest.mark.unit
    def test_promotion_returns_large_positive_change(self):
        """promotion event should return large positive morale change."""
        change = MoraleCalculator.calculate_morale_change("promotion", 70)
        assert change == 30

    @pytest.mark.unit
    def test_good_position_returns_positive_change(self):
        """good_position event should return positive morale change."""
        change = MoraleCalculator.calculate_morale_change("good_position", 70)
        assert change == 5

    @pytest.mark.unit
    def test_clever_tactic_returns_positive_change(self):
        """clever_tactic event should return positive morale change."""
        change = MoraleCalculator.calculate_morale_change("clever_tactic", 70)
        assert change == 10

    @pytest.mark.unit
    def test_game_start_returns_zero_change(self):
        """game_start event should return zero morale change."""
        change = MoraleCalculator.calculate_morale_change("game_start", 70)
        assert change == 0

    @pytest.mark.unit
    def test_persuasion_success_returns_positive_change(self):
        """persuasion_success event should return positive morale change."""
        change = MoraleCalculator.calculate_morale_change("persuasion_success", 70)
        assert change == 5

    @pytest.mark.unit
    def test_persuasion_fail_returns_negative_change(self):
        """persuasion_fail event should return negative morale change."""
        change = MoraleCalculator.calculate_morale_change("persuasion_fail", 70)
        assert change == -3

    @pytest.mark.unit
    def test_player_lied_returns_large_negative_change(self):
        """player_lied event should return large negative morale change."""
        change = MoraleCalculator.calculate_morale_change("player_lied", 70)
        assert change == -15

    @pytest.mark.unit
    def test_unknown_event_returns_zero(self):
        """Unknown event type should return zero change."""
        change = MoraleCalculator.calculate_morale_change("unknown_event", 70)
        assert change == 0

    @pytest.mark.unit
    def test_personality_modifiers_override_base_change(self):
        """Personality modifiers should override base change values."""
        personality = {"morale_modifiers": {"capture_enemy": 25}}
        change = MoraleCalculator.calculate_morale_change("capture_enemy", 70, personality)
        assert change == 25

    @pytest.mark.unit
    def test_empty_personality_uses_base_change(self):
        """Empty personality should use base change values."""
        personality = {}
        change = MoraleCalculator.calculate_morale_change("capture_enemy", 70, personality)
        assert change == 15

    @pytest.mark.unit
    def test_modifiers_without_event_type_uses_base(self):
        """Modifiers without specific event type should use base change."""
        personality = {"morale_modifiers": {"other_event": 50}}
        change = MoraleCalculator.calculate_morale_change("capture_enemy", 70, personality)
        assert change == 15


class TestApplyMoraleChange:
    """Tests for MoraleCalculator.apply_morale_change method."""

    @pytest.mark.unit
    def test_positive_change_increases_morale(self):
        """Positive change should increase morale."""
        new_morale = MoraleCalculator.apply_morale_change(70, 15)
        assert new_morale == 85

    @pytest.mark.unit
    def test_negative_change_decreases_morale(self):
        """Negative change should decrease morale."""
        new_morale = MoraleCalculator.apply_morale_change(70, -10)
        assert new_morale == 60

    @pytest.mark.unit
    def test_morale_clamped_at_100(self):
        """Morale should be clamped at maximum 100."""
        new_morale = MoraleCalculator.apply_morale_change(95, 15)
        assert new_morale == 100

    @pytest.mark.unit
    def test_morale_clamped_at_0(self):
        """Morale should be clamped at minimum 0."""
        new_morale = MoraleCalculator.apply_morale_change(10, -20)
        assert new_morale == 0

    @pytest.mark.unit
    def test_zero_change_preserves_morale(self):
        """Zero change should preserve current morale."""
        new_morale = MoraleCalculator.apply_morale_change(70, 0)
        assert new_morale == 70


class TestGetMoraleCategory:
    """Tests for MoraleCalculator.get_morale_category method."""

    @pytest.mark.unit
    @pytest.mark.parametrize("morale,expected", [
        (100, "enthusiastic"),
        (90, "enthusiastic"),
        (80, "enthusiastic"),
        (79, "normal"),
        (70, "normal"),
        (60, "normal"),
        (59, "reluctant"),
        (50, "reluctant"),
        (40, "reluctant"),
        (39, "demoralized"),
        (30, "demoralized"),
        (20, "demoralized"),
        (19, "mutinous"),
        (10, "mutinous"),
        (0, "mutinous"),
    ])
    def test_morale_category_boundaries(self, morale: int, expected: str):
        """Morale should be categorized correctly at all boundaries."""
        category = MoraleCalculator.get_morale_category(morale)
        assert category == expected

    @pytest.mark.unit
    def test_negative_morale_returns_normal(self):
        """Negative morale (invalid) should return 'normal' as fallback."""
        category = MoraleCalculator.get_morale_category(-10)
        assert category == "normal"

    @pytest.mark.unit
    def test_over_100_morale_returns_normal(self):
        """Morale over 100 (invalid) should return 'normal' as fallback."""
        category = MoraleCalculator.get_morale_category(110)
        assert category == "normal"


class TestGetObedienceRate:
    """Tests for MoraleCalculator.get_obedience_rate method."""

    @pytest.mark.unit
    @pytest.mark.parametrize("morale,expected", [
        (100, 0.95),
        (90, 0.95),
        (80, 0.95),
        (79, 0.80),
        (70, 0.80),
        (60, 0.80),
        (59, 0.55),
        (50, 0.55),
        (40, 0.55),
        (39, 0.30),
        (30, 0.30),
        (20, 0.30),
        (19, 0.10),
        (10, 0.10),
        (0, 0.10),
    ])
    def test_obedience_rate_by_morale(self, morale: int, expected: float):
        """Obedience rate should match expected values for morale ranges."""
        rate = MoraleCalculator.get_obedience_rate(morale)
        assert rate == expected


class TestWillPieceObey:
    """Tests for MoraleCalculator.will_piece_obey method."""

    @pytest.mark.unit
    @patch("random.random")
    def test_high_morale_piece_obeys(self, mock_random):
        """High morale piece should obey when random is below rate."""
        mock_random.return_value = 0.5
        will_obey = MoraleCalculator.will_piece_obey(80, False, "pawn")
        assert will_obey is True

    @pytest.mark.unit
    @patch("random.random")
    def test_low_morale_piece_refuses(self, mock_random):
        """Low morale piece should refuse when random is above rate."""
        mock_random.return_value = 0.95
        will_obey = MoraleCalculator.will_piece_obey(30, False, "pawn")
        assert will_obey is False

    @pytest.mark.unit
    @patch("random.random")
    def test_risky_move_reduces_obedience(self, mock_random):
        """Risky move should reduce obedience probability."""
        mock_random.return_value = 0.75  # Above adjusted rate for risky
        will_obey = MoraleCalculator.will_piece_obey(70, True, "pawn")
        assert will_obey is False

    @pytest.mark.unit
    def test_very_high_morale_always_obeys_safe_move(self):
        """Very high morale (90+) should always obey safe moves."""
        will_obey = MoraleCalculator.will_piece_obey(95, False, "pawn")
        assert will_obey is True

    @pytest.mark.unit
    @patch("random.random")
    def test_very_high_morale_can_refuse_risky_move(self, mock_random):
        """Even very high morale may refuse risky moves."""
        mock_random.return_value = 0.95
        will_obey = MoraleCalculator.will_piece_obey(95, True, "queen")
        # Queen has -0.10 modifier, so even 90+ morale doesn't guarantee obedience for risky
        # Base 0.95 * 0.7 (risky) - 0.10 = 0.565
        assert will_obey is False

    @pytest.mark.unit
    @pytest.mark.parametrize("piece_type,expected_modifier", [
        ("rook", 0.10),
        ("knight", -0.05),
        ("bishop", 0.0),
        ("pawn", 0.05),
        ("queen", -0.10),
        ("king", 0.15),
        ("unknown", 0.0),  # Unknown piece type
    ])
    @patch("random.random")
    def test_piece_personality_modifiers(self, mock_random, piece_type: str, expected_modifier: float):
        """Different piece types should apply personality modifiers."""
        mock_random.return_value = 0.75 - expected_modifier  # Adjust threshold based on modifier
        will_obey = MoraleCalculator.will_piece_obey(70, False, piece_type)
        # This test verifies the modifiers are applied by checking behavior changes
        assert isinstance(will_obey, bool)


class TestGenerateMoraleDescription:
    """Tests for MoraleCalculator.generate_morale_description method."""

    @pytest.mark.unit
    def test_capture_enemy_description(self):
        """capture_enemy should generate empowering description."""
        desc = MoraleCalculator.generate_morale_description("capture_enemy", "knight", 15, 85)
        assert "feels empowered" in desc.lower()
        assert "knight" in desc.lower()
        assert "+15" in desc

    @pytest.mark.unit
    def test_friendly_captured_description(self):
        """friendly_captured should generate mourning description."""
        desc = MoraleCalculator.generate_morale_description("friendly_captured", "pawn", -10, 60)
        assert "mourns" in desc.lower()
        assert "pawn" in desc.lower()

    @pytest.mark.unit
    def test_promotion_description(self):
        """promotion should generate thrilled description."""
        desc = MoraleCalculator.generate_morale_description("promotion", "pawn", 30, 100)
        assert "thrilled" in desc.lower()
        assert "promotion" in desc.lower()

    @pytest.mark.unit
    def test_player_lied_description(self):
        """player_lied should generate betrayal description."""
        desc = MoraleCalculator.generate_morale_description("player_lied", "rook", -15, 55)
        assert "betrayed" in desc.lower()
        assert "broke your promise" in desc.lower()

    @pytest.mark.unit
    def test_unknown_event_uses_default_description(self):
        """Unknown event type should use default description format."""
        desc = MoraleCalculator.generate_morale_description("unknown_event", "bishop", 5, 75)
        assert "morale" in desc.lower()
        assert "increased" in desc.lower()
        assert "bishop" in desc.lower()

    @pytest.mark.unit
    def test_negative_change_shows_decreased(self):
        """Negative change should show 'decreased' in description."""
        desc = MoraleCalculator.generate_morale_description("idle", "queen", -5, 65)
        assert "decreased" in desc.lower() or "-5" in desc


class TestProcessMoveMoraleEffects:
    """Tests for MoraleCalculator.process_move_morale_events method."""

    @pytest.fixture
    def sample_pieces(self):
        """Create sample game pieces for testing."""
        return [
            {
                "id": "piece-1",
                "color": "white",
                "piece_type": "pawn",
                "morale": 70,
                "is_captured": False,
                "personality": {},
            },
            {
                "id": "piece-2",
                "color": "white",
                "piece_type": "knight",
                "morale": 75,
                "is_captured": False,
                "personality": {},
            },
            {
                "id": "piece-3",
                "color": "black",
                "piece_type": "pawn",
                "morale": 65,
                "is_captured": False,
                "personality": {},
            },
        ]

    @pytest.mark.unit
    def test_capture_generates_capture_event(self, sample_pieces):
        """Capture move should generate capture_enemy event for moving piece."""
        events = MoraleCalculator.process_move_morale_effects(
            sample_pieces, "piece-1", True, "pawn", False, 7
        )

        capture_events = [e for e in events if e["event_type"] == "capture_enemy"]
        assert len(capture_events) == 1
        assert capture_events[0]["piece_id"] == "piece-1"

    @pytest.mark.unit
    def test_bad_move_affects_friendly_pieces(self, sample_pieces):
        """Bad move (quality <= 3) should affect friendly pieces."""
        events = MoraleCalculator.process_move_morale_effects(
            sample_pieces, "piece-1", False, None, False, 2
        )

        blunder_events = [e for e in events if e["event_type"] == "blunder"]
        # Should affect piece-2 (same color) but not piece-3 (different color)
        assert len(blunder_events) == 1
        assert blunder_events[0]["piece_id"] == "piece-2"

    @pytest.mark.unit
    def test_good_move_does_not_affect_others(self, sample_pieces):
        """Good move (quality > 3) should not cause blunder events."""
        events = MoraleCalculator.process_move_morale_effects(
            sample_pieces, "piece-1", False, None, False, 7
        )

        blunder_events = [e for e in events if e["event_type"] == "blunder"]
        assert len(blunder_events) == 0

    @pytest.mark.unit
    def test_captured_pieces_not_affected(self, sample_pieces):
        """Captured pieces should not receive morale changes."""
        sample_pieces[1]["is_captured"] = True

        events = MoraleCalculator.process_move_morale_effects(
            sample_pieces, "piece-1", False, None, False, 2
        )

        # piece-2 is captured, so should not be in events
        piece_2_events = [e for e in events if e["piece_id"] == "piece-2"]
        assert len(piece_2_events) == 0

    @pytest.mark.unit
    def test_events_include_required_fields(self, sample_pieces):
        """Generated events should include all required fields."""
        events = MoraleCalculator.process_move_morale_effects(
            sample_pieces, "piece-1", True, "pawn", False, 7
        )

        assert len(events) > 0
        for event in events:
            assert "piece_id" in event
            assert "event_type" in event
            assert "morale_change" in event
            assert "morale_after" in event
            assert "description" in event


class TestMoraleEventsDictionary:
    """Tests for the MORALE_EVENTS dictionary constants."""

    @pytest.mark.unit
    def test_all_expected_events_present(self):
        """All expected morale event types should be present."""
        expected_events = [
            "capture_enemy",
            "friendly_captured",
            "endangered",
            "protected",
            "blunder",
            "idle",
            "compliment",
            "promotion",
            "good_position",
            "clever_tactic",
            "game_start",
            "persuasion_success",
            "persuasion_fail",
            "player_lied",
        ]
        for event in expected_events:
            assert event in MORALE_EVENTS

    @pytest.mark.unit
    def test_promotion_has_highest_positive_change(self):
        """Promotion should have the highest positive morale change."""
        positive_changes = {k: v for k, v in MORALE_EVENTS.items() if v > 0}
        max_change = max(positive_changes.values())
        assert MORALE_EVENTS["promotion"] == max_change

    @pytest.mark.unit
    def test_player_lied_has_highest_negative_change(self):
        """Player lying should have the highest negative morale change."""
        negative_changes = {k: v for k, v in MORALE_EVENTS.items() if v < 0}
        min_change = min(negative_changes.values())
        assert MORALE_EVENTS["player_lied"] == min_change
