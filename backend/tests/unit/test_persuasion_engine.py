"""Unit tests for the persuasion engine service."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.persuasion_engine import PersuasionEngine, BASE_RATES, PERSONALITY_KEYWORDS


class TestGetBaseRate:
    """Tests for PersuasionEngine.get_base_rate method."""

    @pytest.mark.unit
    @pytest.mark.parametrize("morale,expected", [
        (100, 0.90),
        (90, 0.90),
        (80, 0.90),
        (79, 0.70),
        (70, 0.70),
        (60, 0.70),
        (59, 0.45),
        (50, 0.45),
        (40, 0.45),
        (39, 0.25),
        (30, 0.25),
        (20, 0.25),
        (19, 0.10),
        (10, 0.10),
        (0, 0.10),
    ])
    def test_base_rate_by_morale_range(self, morale: int, expected: float):
        """Base rate should match expected values for morale ranges."""
        rate = PersuasionEngine.get_base_rate(morale)
        assert rate == expected

    @pytest.mark.unit
    def test_default_rate_for_out_of_range(self):
        """Out of range morale should return default rate of 0.45."""
        rate = PersuasionEngine.get_base_rate(-10)
        assert rate == 0.45

        rate = PersuasionEngine.get_base_rate(150)
        assert rate == 0.45


class TestCalculateLogicScore:
    """Tests for PersuasionEngine.calculate_logic_score method."""

    @pytest.mark.unit
    def test_base_score_for_any_argument(self):
        """Any argument should receive a base score of 5."""
        score = PersuasionEngine.calculate_logic_score("Short arg", True, False)
        assert score >= 5

    @pytest.mark.unit
    def test_accurate_claim_adds_bonus(self):
        """Accurate claim should add 10 point bonus."""
        score_accurate = PersuasionEngine.calculate_logic_score("Argument", True, False)
        score_inaccurate = PersuasionEngine.calculate_logic_score("Argument", False, False)
        assert score_accurate == score_inaccurate + 15  # 10 bonus + 5 not subtracted

    @pytest.mark.unit
    def test_inaccurate_claim_penalty(self):
        """Inaccurate claim should subtract 5 points."""
        score = PersuasionEngine.calculate_logic_score("Argument", False, False)
        # Base 5 - 5 penalty = 0
        assert score == 0

    @pytest.mark.unit
    def test_long_argument_bonus(self):
        """Argument with 10+ words should get bonus."""
        short_score = PersuasionEngine.calculate_logic_score("Short arg", True, False)
        long_score = PersuasionEngine.calculate_logic_score(
            "This is a much longer argument with many words for testing", True, False
        )
        assert long_score > short_score

    @pytest.mark.unit
    def test_medium_argument_partial_bonus(self):
        """Argument with 5-9 words should get partial bonus."""
        short_score = PersuasionEngine.calculate_logic_score("Short arg", True, False)
        medium_score = PersuasionEngine.calculate_logic_score(
            "This argument has five words", True, False
        )
        assert medium_score > short_score

    @pytest.mark.unit
    def test_risky_acknowledgment_bonus(self):
        """Acknowledging risk in argument should add bonus."""
        base_score = PersuasionEngine.calculate_logic_score(
            "Make this move", True, True
        )
        acknowledged_score = PersuasionEngine.calculate_logic_score(
            "This risky move is dangerous", True, True
        )
        assert acknowledged_score > base_score

    @pytest.mark.unit
    def test_score_clamped_at_25(self):
        """Logic score should be capped at 25."""
        score = PersuasionEngine.calculate_logic_score(
            "This is a very long and detailed argument that acknowledges the risky sacrifice "
            "and trade while being completely accurate in all claims made",
            True, True
        )
        assert score == 25

    @pytest.mark.unit
    def test_score_minimum_is_zero(self):
        """Logic score should have minimum of 0."""
        score = PersuasionEngine.calculate_logic_score("", False, False)
        assert score == 0


class TestCalculatePersonalityMatch:
    """Tests for PersuasionEngine.calculate_personality_match method."""

    @pytest.mark.unit
    def test_knight_responds_to_glory_keywords(self):
        """Knight should respond to glory-related keywords."""
        score = PersuasionEngine.calculate_personality_match(
            "For glory and honor, charge!", "knight"
        )
        assert score == 15

    @pytest.mark.unit
    def test_bishop_responds_to_logic_keywords(self):
        """Bishop should respond to logic-related keywords."""
        score = PersuasionEngine.calculate_personality_match(
            "This is the logical tactical strategy", "bishop"
        )
        assert score == 15

    @pytest.mark.unit
    def test_rook_responds_to_duty_keywords(self):
        """Rook should respond to duty-related keywords."""
        score = PersuasionEngine.calculate_personality_match(
            "Your duty is to defend and hold strong", "rook"
        )
        assert score == 15

    @pytest.mark.unit
    def test_queen_responds_to_power_keywords(self):
        """Queen should respond to power-related keywords."""
        score = PersuasionEngine.calculate_personality_match(
            "Your power is important to protect", "queen"
        )
        assert score == 15

    @pytest.mark.unit
    def test_pawn_responds_to_team_keywords(self):
        """Pawn should respond to team-related keywords."""
        score = PersuasionEngine.calculate_personality_match(
            "For the team and our greater good together", "pawn"
        )
        assert score == 15

    @pytest.mark.unit
    def test_king_responds_to_safety_keywords(self):
        """King should respond to safety-related keywords."""
        score = PersuasionEngine.calculate_personality_match(
            "Protect your safety and the kingdom", "king"
        )
        assert score == 15

    @pytest.mark.unit
    def test_partial_match_scores_less(self):
        """Partial keyword match should score less than full match."""
        full_score = PersuasionEngine.calculate_personality_match(
            "glory brave honor charge", "knight"
        )
        partial_score = PersuasionEngine.calculate_personality_match(
            "glory brave", "knight"
        )
        single_score = PersuasionEngine.calculate_personality_match(
            "glory", "knight"
        )
        assert full_score > partial_score > single_score

    @pytest.mark.unit
    def test_no_match_gets_minimum_score(self):
        """No keyword match should get minimum score of 2."""
        score = PersuasionEngine.calculate_personality_match(
            "This argument has no relevant keywords", "knight"
        )
        assert score == 2

    @pytest.mark.unit
    def test_unknown_piece_type_gets_minimum(self):
        """Unknown piece type should get minimum score."""
        score = PersuasionEngine.calculate_personality_match(
            "glory brave honor", "unknown_piece"
        )
        assert score == 2


class TestCalculateMoraleModifier:
    """Tests for PersuasionEngine.calculate_morale_modifier method."""

    @pytest.mark.unit
    @pytest.mark.parametrize("morale,expected", [
        (100, 20),
        (90, 20),
        (80, 20),
        (79, 10),
        (70, 10),
        (60, 10),
        (59, 0),
        (50, 0),
        (40, 0),
        (39, -10),
        (30, -10),
        (20, -10),
        (19, -20),
        (10, -20),
        (0, -20),
    ])
    def test_morale_modifier_by_range(self, morale: int, expected: int):
        """Morale modifier should match expected values."""
        modifier = PersuasionEngine.calculate_morale_modifier(morale)
        assert modifier == expected


class TestCalculateTrustModifier:
    """Tests for PersuasionEngine.calculate_trust_modifier method."""

    @pytest.mark.unit
    @pytest.mark.parametrize("trust_history,expected", [
        (1.0, 10),
        (0.9, 10),
        (0.8, 10),
        (0.79, 5),
        (0.7, 5),
        (0.6, 5),
        (0.59, 0),
        (0.5, 0),
        (0.4, 0),
        (0.39, -8),
        (0.3, -8),
        (0.2, -8),
        (0.19, -15),
        (0.1, -15),
        (0.0, -15),
    ])
    def test_trust_modifier_by_history(self, trust_history: float, expected: int):
        """Trust modifier should match expected values."""
        modifier = PersuasionEngine.calculate_trust_modifier(trust_history)
        assert modifier == expected


class TestCalculateUrgencyFactor:
    """Tests for PersuasionEngine.calculate_urgency_factor method."""

    @pytest.mark.unit
    def test_check_adds_urgency(self):
        """Being in check should add urgency."""
        no_check = PersuasionEngine.calculate_urgency_factor(False, 0, 10)
        in_check = PersuasionEngine.calculate_urgency_factor(True, 0, 10)
        assert in_check > no_check

    @pytest.mark.unit
    def test_large_material_deficit_adds_urgency(self):
        """Large material deficit should add urgency."""
        even = PersuasionEngine.calculate_urgency_factor(False, 0, 10)
        down_material = PersuasionEngine.calculate_urgency_factor(False, -5, 10)
        assert down_material > even

    @pytest.mark.unit
    def test_small_material_deficit_adds_less_urgency(self):
        """Small material deficit should add less urgency."""
        even = PersuasionEngine.calculate_urgency_factor(False, 0, 10)
        slight_down = PersuasionEngine.calculate_urgency_factor(False, -1, 10)
        assert slight_down > even

    @pytest.mark.unit
    def test_late_game_adds_urgency(self):
        """Late game (40+ moves) should add urgency."""
        early = PersuasionEngine.calculate_urgency_factor(False, 0, 10)
        late = PersuasionEngine.calculate_urgency_factor(False, 0, 50)
        assert late > early

    @pytest.mark.unit
    def test_urgency_clamped_at_10(self):
        """Urgency factor should be capped at 10."""
        urgency = PersuasionEngine.calculate_urgency_factor(True, -5, 50)
        assert urgency == 10


class TestEvaluatePersuasion:
    """Tests for PersuasionEngine.evaluate_persuasion method."""

    @pytest.mark.unit
    @patch("random.random")
    def test_high_probability_success(self, mock_random):
        """High probability persuasion should succeed."""
        mock_random.return_value = 0.1  # Below high probability
        result = PersuasionEngine.evaluate_persuasion(
            argument="For glory and honor!",
            piece_type="knight",
            morale=90,
            is_claim_accurate=True,
            is_risky=False,
            trust_history=0.9,
        )
        assert result["success"] is True

    @pytest.mark.unit
    @patch("random.random")
    def test_low_probability_failure(self, mock_random):
        """Low probability persuasion should fail."""
        mock_random.return_value = 0.95  # Above low probability
        result = PersuasionEngine.evaluate_persuasion(
            argument="Bad argument",
            piece_type="knight",
            morale=10,
            is_claim_accurate=False,
            is_risky=True,
            trust_history=0.1,
        )
        assert result["success"] is False

    @pytest.mark.unit
    def test_result_includes_all_factors(self):
        """Result should include all evaluation factors."""
        result = PersuasionEngine.evaluate_persuasion(
            argument="Test argument",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=True,
            is_risky=False,
        )

        assert "success" in result
        assert "probability" in result
        assert "logic_score" in result
        assert "personality_match" in result
        assert "morale_modifier" in result
        assert "trust_modifier" in result
        assert "urgency_factor" in result

    @pytest.mark.unit
    def test_probability_within_valid_range(self):
        """Probability should be between 0.05 and 0.95."""
        result = PersuasionEngine.evaluate_persuasion(
            argument="Test",
            piece_type="pawn",
            morale=50,
            is_claim_accurate=True,
            is_risky=False,
        )

        assert 0.05 <= result["probability"] <= 0.95

    @pytest.mark.unit
    def test_high_morale_increases_probability(self):
        """High morale should increase success probability."""
        high_morale = PersuasionEngine.evaluate_persuasion(
            argument="Test argument",
            piece_type="pawn",
            morale=90,
            is_claim_accurate=True,
            is_risky=False,
        )
        low_morale = PersuasionEngine.evaluate_persuasion(
            argument="Test argument",
            piece_type="pawn",
            morale=10,
            is_claim_accurate=True,
            is_risky=False,
        )
        assert high_morale["probability"] > low_morale["probability"]

    @pytest.mark.unit
    def test_accurate_claims_increase_probability(self):
        """Accurate claims should increase success probability."""
        accurate = PersuasionEngine.evaluate_persuasion(
            argument="Test argument",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=True,
            is_risky=False,
        )
        inaccurate = PersuasionEngine.evaluate_persuasion(
            argument="Test argument",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=False,
            is_risky=False,
        )
        assert accurate["probability"] > inaccurate["probability"]

    @pytest.mark.unit
    def test_personality_match_increases_probability(self):
        """Matching personality keywords should increase probability."""
        matched = PersuasionEngine.evaluate_persuasion(
            argument="For the team and greater good!",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=True,
            is_risky=False,
        )
        unmatched = PersuasionEngine.evaluate_persuasion(
            argument="Generic argument",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=True,
            is_risky=False,
        )
        assert matched["probability"] > unmatched["probability"]

    @pytest.mark.unit
    def test_trust_history_affects_probability(self):
        """Trust history should affect success probability."""
        high_trust = PersuasionEngine.evaluate_persuasion(
            argument="Test",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=True,
            is_risky=False,
            trust_history=0.9,
        )
        low_trust = PersuasionEngine.evaluate_persuasion(
            argument="Test",
            piece_type="pawn",
            morale=70,
            is_claim_accurate=True,
            is_risky=False,
            trust_history=0.1,
        )
        assert high_trust["probability"] > low_trust["probability"]


class TestPersonalityKeywords:
    """Tests for the PERSONALITY_KEYWORDS dictionary."""

    @pytest.mark.unit
    def test_all_standard_pieces_have_keywords(self):
        """All standard piece types should have personality keywords."""
        standard_pieces = ["pawn", "knight", "bishop", "rook", "queen", "king"]
        for piece in standard_pieces:
            assert piece in PERSONALITY_KEYWORDS
            assert len(PERSONALITY_KEYWORDS[piece]) > 0

    @pytest.mark.unit
    def test_knight_keywords_include_glory(self):
        """Knight keywords should include glory-related terms."""
        assert "glory" in PERSONALITY_KEYWORDS["knight"]
        assert "brave" in PERSONALITY_KEYWORDS["knight"]
        assert "honor" in PERSONALITY_KEYWORDS["knight"]

    @pytest.mark.unit
    def test_bishop_keywords_include_logic(self):
        """Bishop keywords should include logic-related terms."""
        assert "logic" in PERSONALITY_KEYWORDS["bishop"]
        assert "tactical" in PERSONALITY_KEYWORDS["bishop"]
        assert "strategy" in PERSONALITY_KEYWORDS["bishop"]

    @pytest.mark.unit
    def test_pawn_keywords_include_team(self):
        """Pawn keywords should include team-related terms."""
        assert "team" in PERSONALITY_KEYWORDS["pawn"]
        assert "sacrifice" in PERSONALITY_KEYWORDS["pawn"]
        assert "duty" in PERSONALITY_KEYWORDS["pawn"]


class TestBaseRates:
    """Tests for the BASE_RATES dictionary."""

    @pytest.mark.unit
    def test_base_rates_cover_full_range(self):
        """Base rates should cover full morale range 0-100."""
        ranges = list(BASE_RATES.keys())
        # Check that ranges are contiguous
        sorted_ranges = sorted(ranges, key=lambda x: x[0], reverse=True)
        for i in range(len(sorted_ranges) - 1):
            assert sorted_ranges[i][1] == sorted_ranges[i + 1][0] - 1

    @pytest.mark.unit
    def test_rates_decrease_with_morale(self):
        """Base rates should decrease as morale decreases."""
        rates = [rate for (_, rate) in sorted(BASE_RATES.items(), key=lambda x: x[0][0], reverse=True)]
        for i in range(len(rates) - 1):
            assert rates[i] > rates[i + 1]
