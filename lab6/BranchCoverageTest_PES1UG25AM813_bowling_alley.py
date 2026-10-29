"""
Lab 6 – Branch Coverage Test Suite
Application : bowling_alley.py
Student ID  : PES1UG25AM813
Target      : ≥ 90% branch coverage

Run:
    cd lab6
    coverage run --source=bowling_alley --branch -m pytest BranchCoverageTest_PES1UG25AM813_bowling_alley.py -v
    coverage report -m

Branch map (True / False for every condition):
─────────────────────────────────────────────────────────────────────────────
lane_cost
  B1 : day_type not in LANE_RATE              → True (raise) / False (ok)
  B2 : games < 1 or players < 1 or players>6 → True (raise) / False (ok)
  B3 : shoe_rentals > players                 → True (raise) / False (ok)
  B4 : players > 4                            → True (+100*games)/ False
  B5 : is_league_member                       → True (discount) / False

frame_score
  B6 : first_roll < 0                        → True (raise)  / False
  B7 : first_roll > 10                        → True (raise)  / False
  B8 : second_roll < 0                        → True (raise)  / False
  B9 : first_roll == 10 (strike)              → True / False
  B10: first+second > 10                      → True (raise)  / False
  B11: first+second == 10 (spare)             → True / False
  (final return is the "else" of B11)

lane_assignment
  B12: lanes_free == 0                        → True (wait)   / False
  B13: has_kids                               → True (bumper) / False
  B14: players > 6 and lanes_free >= 2        → True (two)    / False
  B15: players > 6 (elif, lanes_free<2)       → True (wait)   / False
  (final return covers the False of B15)
─────────────────────────────────────────────────────────────────────────────
"""

import pytest
from bowling_alley import lane_cost, frame_score, lane_assignment

# ---------------------------------------------------------------------------
# lane_cost – branch-by-branch
# ---------------------------------------------------------------------------

class TestLaneCostBranches:

    # B1 – day_type not in LANE_RATE
    def test_B1_true_unknown_day(self):
        """B1 True: unknown day_type raises ValueError."""
        with pytest.raises(ValueError, match="unknown day type"):
            lane_cost("sunday", 1, 2, 0, False)

    def test_B1_false_weekday(self):
        """B1 False: valid 'weekday' passes the guard."""
        result = lane_cost("weekday", 1, 2, 0, False)
        assert result == 400

    def test_B1_false_weekend(self):
        """B1 False: valid 'weekend' passes the guard."""
        result = lane_cost("weekend", 1, 2, 0, False)
        assert result == 600

    # B2 – games < 1 or players < 1 or players > 6
    def test_B2_true_games_zero(self):
        """B2 True: games == 0 triggers invalid booking."""
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", 0, 1, 0, False)

    def test_B2_true_games_negative(self):
        """B2 True: games < 0 triggers invalid booking."""
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", -3, 1, 0, False)

    def test_B2_true_players_zero(self):
        """B2 True: players == 0 triggers invalid booking."""
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", 1, 0, 0, False)

    def test_B2_true_players_too_many(self):
        """B2 True: players == 7 triggers invalid booking."""
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", 1, 7, 0, False)

    def test_B2_false_valid_booking(self):
        """B2 False: valid games and players (1 game, 6 players)."""
        result = lane_cost("weekday", 1, 6, 0, False)
        # 400 + 100 surcharge for 5+ players
        assert result == 500

    # B3 – shoe_rentals > players
    def test_B3_true_too_many_shoes(self):
        """B3 True: shoe_rentals (3) > players (2) raises."""
        with pytest.raises(ValueError, match="too many shoe rentals"):
            lane_cost("weekday", 1, 2, 3, False)

    def test_B3_false_shoes_equal_players(self):
        """B3 False: shoe_rentals == players is allowed."""
        result = lane_cost("weekday", 1, 4, 4, False)
        assert result == 600  # 400 + 4*50

    def test_B3_false_shoes_less_than_players(self):
        """B3 False: shoe_rentals < players is allowed."""
        result = lane_cost("weekday", 1, 4, 2, False)
        assert result == 500  # 400 + 2*50

    # B4 – players > 4
    def test_B4_true_5_players(self):
        """B4 True: 5 players → surcharge applied."""
        result = lane_cost("weekday", 2, 5, 0, False)
        assert result == 1000  # (400+100)*2

    def test_B4_true_6_players(self):
        """B4 True: 6 players → surcharge applied."""
        result = lane_cost("weekday", 2, 6, 0, False)
        assert result == 1000

    def test_B4_false_4_players(self):
        """B4 False: exactly 4 players → no surcharge."""
        result = lane_cost("weekday", 2, 4, 0, False)
        assert result == 800  # 400*2

    def test_B4_false_1_player(self):
        """B4 False: 1 player → no surcharge."""
        result = lane_cost("weekday", 1, 1, 0, False)
        assert result == 400

    # B5 – is_league_member
    def test_B5_true_discount_applied(self):
        """B5 True: league member gets 1/5 discount."""
        # 400*1 = 400; 400//5 = 80; 400-80 = 320
        result = lane_cost("weekday", 1, 2, 0, True)
        assert result == 320

    def test_B5_false_no_discount(self):
        """B5 False: non-member pays full price."""
        result = lane_cost("weekday", 1, 2, 0, False)
        assert result == 400


# ---------------------------------------------------------------------------
# frame_score – branch-by-branch
# ---------------------------------------------------------------------------

class TestFrameScoreBranches:

    # B6 – first_roll < 0
    def test_B6_true_negative_first(self):
        """B6 True: first_roll negative → invalid roll."""
        with pytest.raises(ValueError, match="invalid roll"):
            frame_score(-1, 5, [])

    def test_B6_false_zero_first(self):
        """B6 False: first_roll == 0 passes the < 0 check."""
        assert frame_score(0, 5, []) == 5

    # B7 – first_roll > 10
    def test_B7_true_first_over_10(self):
        """B7 True: first_roll == 11 → invalid roll."""
        with pytest.raises(ValueError, match="invalid roll"):
            frame_score(11, 0, [])

    def test_B7_false_first_equals_10(self):
        """B7 False: first_roll == 10 is valid (strike path)."""
        assert frame_score(10, 0, [3, 4]) == 17

    # B8 – second_roll < 0
    def test_B8_true_negative_second(self):
        """B8 True: second_roll negative → invalid roll."""
        with pytest.raises(ValueError, match="invalid roll"):
            frame_score(3, -1, [])

    def test_B8_false_zero_second(self):
        """B8 False: second_roll == 0 is valid."""
        assert frame_score(3, 0, []) == 3

    # B9 – first_roll == 10 (strike)
    def test_B9_true_strike(self):
        """B9 True: strike → returns 10 + bonus[0] + bonus[1]."""
        assert frame_score(10, 0, [5, 3]) == 18

    def test_B9_false_not_strike(self):
        """B9 False: first_roll != 10 → falls through to spare/open check."""
        assert frame_score(7, 3, [6]) == 16   # spare

    # B10 – first + second > 10 (invalid frame, not strike)
    def test_B10_true_over_10_non_strike(self):
        """B10 True: 6+5 > 10 and first_roll≠10 → invalid frame."""
        with pytest.raises(ValueError, match="invalid frame"):
            frame_score(6, 5, [])

    def test_B10_false_spare(self):
        """B10 False: 6+4 == 10 (spare) – sum ≤ 10 so no raise."""
        assert frame_score(6, 4, [3]) == 13

    def test_B10_false_open_frame(self):
        """B10 False: 4+3 < 10 – open frame, no raise."""
        assert frame_score(4, 3, []) == 7

    # B11 – first + second == 10 (spare)
    def test_B11_true_spare(self):
        """B11 True: spare → returns 10 + bonus[0]."""
        assert frame_score(7, 3, [4, 9]) == 14

    def test_B11_true_spare_zero_bonus(self):
        """B11 True: spare with 0 bonus."""
        assert frame_score(5, 5, [0]) == 10

    def test_B11_false_open_frame(self):
        """B11 False: open frame (sum < 10) → returns sum only."""
        assert frame_score(3, 4, []) == 7

    def test_B11_false_open_zero(self):
        """B11 False: 0+0 = 0 open frame."""
        assert frame_score(0, 0, []) == 0


# ---------------------------------------------------------------------------
# lane_assignment – branch-by-branch
# ---------------------------------------------------------------------------

class TestLaneAssignmentBranches:

    # B12 – lanes_free == 0
    def test_B12_true_no_free_lanes(self):
        """B12 True: lanes_free == 0 → 'wait'."""
        assert lane_assignment(2, False, 0) == "wait"

    def test_B12_true_kids_but_no_lanes(self):
        """B12 True: even with kids, no lanes → 'wait'."""
        assert lane_assignment(3, True, 0) == "wait"

    def test_B12_false_lanes_available(self):
        """B12 False: lanes_free > 0 falls through."""
        # standard case
        assert lane_assignment(4, False, 1) == "standard lane"

    # B13 – has_kids
    def test_B13_true_bumper_lane(self):
        """B13 True: has_kids → 'bumper lane'."""
        assert lane_assignment(2, True, 1) == "bumper lane"

    def test_B13_true_kids_overrides_large_group(self):
        """B13 True: kids flag overrides the large-group logic."""
        assert lane_assignment(8, True, 4) == "bumper lane"

    def test_B13_false_no_kids(self):
        """B13 False: no kids → continues to next check."""
        assert lane_assignment(4, False, 2) == "standard lane"

    # B14 – players > 6 AND lanes_free >= 2
    def test_B14_true_two_lanes_assigned(self):
        """B14 True: 7 players and 2 free lanes → 'two lanes'."""
        assert lane_assignment(7, False, 2) == "two lanes"

    def test_B14_true_many_players_many_lanes(self):
        """B14 True: 10 players and 3 free lanes → 'two lanes'."""
        assert lane_assignment(10, False, 3) == "two lanes"

    def test_B14_false_small_group(self):
        """B14 False: players ≤ 6 → standard lane."""
        assert lane_assignment(6, False, 2) == "standard lane"

    # B15 – elif players > 6 (lanes_free < 2, i.e. lanes_free == 1)
    def test_B15_true_large_group_one_lane(self):
        """B15 True: 7 players but only 1 lane → 'wait'."""
        assert lane_assignment(7, False, 1) == "wait"

    def test_B15_false_small_group_one_lane(self):
        """B15 False: ≤6 players, 1 lane → 'standard lane'."""
        assert lane_assignment(5, False, 1) == "standard lane"

    def test_B15_false_exactly_6_one_lane(self):
        """B15 False: exactly 6 players, 1 lane → 'standard lane'."""
        assert lane_assignment(6, False, 1) == "standard lane"
