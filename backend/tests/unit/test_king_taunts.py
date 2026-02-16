"""Unit tests for the King taunt generator service."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.king_taunts import KingTauntGenerator, TAUNTS


class TestGenerateTaunt:
    """Tests for KingTauntGenerator.generate_taunt method."""

    @pytest.mark.unit
    def test_generate_taunt_for_check(self):
        """Should generate taunt for check event."""
        taunt = KingTauntGenerator.generate_taunt("check")
        assert taunt is not None
        assert isinstance(taunt, str)
        assert len(taunt) > 0

    @pytest.mark.unit
    def test_generate_taunt_for_blunder(self):
        """Should generate taunt for blunder event."""
        taunt = KingTauntGenerator.generate_taunt("blunder")
        assert taunt is not None
        assert isinstance(taunt, str)

    @pytest.mark.unit
    def test_generate_taunt_for_piece_captured(self):
        """Should generate taunt for piece_captured event."""
        taunt = KingTauntGenerator.generate_taunt("piece_captured", piece_type="knight")
        assert taunt is not None
        assert "Knight" in taunt or "piece" in taunt.lower()

    @pytest.mark.unit
    def test_generate_taunt_for_game_start(self):
        """Should generate taunt for game_start event."""
        taunt = KingTauntGenerator.generate_taunt("game_start")
        assert taunt is not None
        assert isinstance(taunt, str)

    @pytest.mark.unit
    def test_generate_taunt_for_winning(self):
        """Should generate taunt when material_balance > 3."""
        taunt = KingTauntGenerator.generate_taunt("other_event", material_balance=5)
        assert taunt is not None

    @pytest.mark.unit
    def test_generate_taunt_for_losing(self):
        """Should generate taunt when material_balance < -3."""
        taunt = KingTauntGenerator.generate_taunt("other_event", material_balance=-5)
        assert taunt is not None

    @pytest.mark.unit
    def test_no_taunt_for_neutral_state(self):
        """Should return None for neutral game state."""
        taunt = KingTauntGenerator.generate_taunt("unknown_event", material_balance=0)
        assert taunt is None

    @pytest.mark.unit
    def test_piece_type_substitution(self):
        """Should substitute {piece} with actual piece type."""
        taunt = KingTauntGenerator.generate_taunt("piece_captured", piece_type="queen")
        assert "Queen" in taunt

    @pytest.mark.unit
    def test_default_piece_substitution(self):
        """Should use 'piece' when no piece_type provided."""
        taunt = KingTauntGenerator.generate_taunt("piece_captured")
        assert "piece" in taunt.lower()

    @pytest.mark.unit
    def test_different_taunts_from_same_category(self):
        """Should potentially return different taunts from same category."""
        taunts = set()
        for _ in range(20):
            taunt = KingTauntGenerator.generate_taunt("check")
            if taunt:
                taunts.add(taunt)
        # Should have multiple different taunts possible
        assert len(taunts) > 1


class TestShouldTaunt:
    """Tests for KingTauntGenerator.should_taunt method."""

    @pytest.mark.unit
    def test_should_taunt_on_check(self):
        """Should always taunt on check."""
        result = KingTauntGenerator.should_taunt("check", 10)
        assert result is True

    @pytest.mark.unit
    def test_should_taunt_on_blunder(self):
        """Should always taunt on blunder."""
        result = KingTauntGenerator.should_taunt("blunder", 10)
        assert result is True

    @pytest.mark.unit
    def test_should_taunt_on_game_start(self):
        """Should always taunt on game_start."""
        result = KingTauntGenerator.should_taunt("game_start", 0)
        assert result is True

    @pytest.mark.unit
    def test_should_taunt_on_piece_captured(self):
        """Should always taunt on piece_captured."""
        result = KingTauntGenerator.should_taunt("piece_captured", 15)
        assert result is True

    @pytest.mark.unit
    @patch("random.random")
    def test_occasional_taunt_for_other_events(self, mock_random):
        """Should occasionally taunt for other events (30% chance)."""
        mock_random.return_value = 0.2  # Below 0.3 threshold
        result = KingTauntGenerator.should_taunt("random_event", 20)
        assert result is True

    @pytest.mark.unit
    @patch("random.random")
    def test_no_taunt_when_random_high(self, mock_random):
        """Should not taunt when random is above threshold."""
        mock_random.return_value = 0.5  # Above 0.3 threshold
        result = KingTauntGenerator.should_taunt("random_event", 20)
        assert result is False


class TestGetTauntIntensity:
    """Tests for KingTauntGenerator.get_taunt_intensity method."""

    @pytest.mark.unit
    def test_check_has_high_intensity(self):
        """Check event should have high intensity."""
        intensity = KingTauntGenerator.get_taunt_intensity(0, "check")
        assert intensity >= 4

    @pytest.mark.unit
    def test_blunder_has_high_intensity(self):
        """Blunder event should have high intensity."""
        intensity = KingTauntGenerator.get_taunt_intensity(0, "blunder")
        assert intensity >= 4

    @pytest.mark.unit
    def test_piece_captured_has_medium_intensity(self):
        """Piece captured should have medium intensity."""
        intensity = KingTauntGenerator.get_taunt_intensity(0, "piece_captured")
        assert intensity == 3

    @pytest.mark.unit
    def test_great_move_has_low_intensity(self):
        """Great move should have low intensity (grudging respect)."""
        intensity = KingTauntGenerator.get_taunt_intensity(0, "great_move")
        assert intensity == 1

    @pytest.mark.unit
    def test_default_intensity_is_two(self):
        """Default intensity should be 2."""
        intensity = KingTauntGenerator.get_taunt_intensity(0, "unknown_event")
        assert intensity == 2

    @pytest.mark.unit
    def test_large_material_advantage_increases_intensity(self):
        """Large material advantage should increase intensity."""
        base_intensity = KingTauntGenerator.get_taunt_intensity(0, "piece_captured")
        high_advantage = KingTauntGenerator.get_taunt_intensity(6, "piece_captured")
        assert high_advantage > base_intensity

    @pytest.mark.unit
    def test_intensity_capped_at_five(self):
        """Intensity should be capped at 5."""
        intensity = KingTauntGenerator.get_taunt_intensity(10, "check")
        assert intensity == 5


class TestTauntsDictionary:
    """Tests for the TAUNTS dictionary."""

    @pytest.mark.unit
    def test_all_categories_have_taunts(self):
        """All taunt categories should have at least one taunt."""
        for category, taunts in TAUNTS.items():
            assert len(taunts) > 0, f"Category {category} has no taunts"

    @pytest.mark.unit
    def test_piece_captured_has_piece_placeholder(self):
        """Piece captured taunts should have {piece} placeholder."""
        for taunt in TAUNTS["piece_captured"]:
            assert "{piece}" in taunt

    @pytest.mark.unit
    def test_blunder_has_piece_placeholder(self):
        """Blunder taunts should have {piece} placeholder."""
        for taunt in TAUNTS["blunder"]:
            assert "{piece}" in taunt

    @pytest.mark.unit
    def test_check_taunts_no_placeholder(self):
        """Check taunts should not need piece placeholder."""
        for taunt in TAUNTS["check"]:
            assert "{piece}" not in taunt

    @pytest.mark.unit
    def test_taunts_are_not_empty(self):
        """No taunt should be empty string."""
        for category, taunts in TAUNTS.items():
            for taunt in taunts:
                assert len(taunt.strip()) > 0, f"Empty taunt in {category}"


class TestIntegration:
    """Integration tests for the taunt generator."""

    @pytest.mark.unit
    def test_full_taunt_workflow(self):
        """Test complete taunt generation workflow."""
        # Check if we should taunt
        if KingTauntGenerator.should_taunt("check", 10):
            # Generate the taunt
            taunt = KingTauntGenerator.generate_taunt("check")
            # Get intensity
            intensity = KingTauntGenerator.get_taunt_intensity(0, "check")

            assert taunt is not None
            assert isinstance(intensity, int)
            assert 1 <= intensity <= 5
