"""
Lab 6 – Code Coverage Test Suite
Application : bowling_alley.py
Student ID  : PES1UG25AM813
Target      : ≥ 90% statement (line) coverage

Run:
    cd lab6
    coverage run --source=bowling_alley -m pytest CodeCoverageTest_PES1UG25AM813_bowling_alley.py -v
    coverage report -m
"""

import pytest
from bowling_alley import lane_cost, frame_score, lane_assignment

# ---------------------------------------------------------------------------
# lane_cost tests
# ---------------------------------------------------------------------------

class TestLaneCostBasic:
    """Happy-path tests – exercises the main statement paths."""

    def test_weekday_no_extras(self):
        # 400 * 1 game, 0 shoe rentals, no member discount, ≤4 players
        assert lane_cost("weekday", 1, 2, 0, False) == 400

    def test_weekend_no_extras(self):
        # 600 * 2 games = 1200
        assert lane_cost("weekend", 2, 3, 0, False) == 1200

    def test_shoe_rentals_added(self):
        # 400 * 1 + 2 * 50 = 500
        assert lane_cost("weekday", 1, 4, 2, False) == 500

    def test_players_over_4_surcharge(self):
        # 400 * 2 + 100 * 2 (surcharge) + 0 shoes = 1000
        assert lane_cost("weekday", 2, 5, 0, False) == 1000

    def test_players_over_4_with_shoes(self):
        # 400*2 + 100*2 + 3*50 = 1150
        assert lane_cost("weekday", 2, 5, 3, False) == 1150

    def test_league_member_discount(self):
        # base = 400*1 = 400; discount = 400//5 = 80; final = 320
        assert lane_cost("weekday", 1, 2, 0, True) == 320

    def test_league_member_with_surcharge_and_shoes(self):
        # base = 400*2 + 100*2 + 2*50 = 1100; discount = 1100//5 = 220; final = 880
        assert lane_cost("weekday", 2, 5, 2, True) == 880

    def test_weekend_league_member(self):
        # base = 600*3 = 1800; discount = 1800//5 = 360; final = 1440
        assert lane_cost("weekend", 3, 4, 0, True) == 1440

    def test_minimum_players_and_games(self):
        # boundary: 1 game, 1 player
        assert lane_cost("weekday", 1, 1, 0, False) == 400

    def test_maximum_players_boundary_4(self):
        # exactly 4 players – no surcharge
        assert lane_cost("weekday", 1, 4, 0, False) == 400

    def test_players_exactly_5(self):
        # 5 players -> surcharge fires: 400 + 100 = 500
        assert lane_cost("weekday", 1, 5, 0, False) == 500

    def test_players_exactly_6(self):
        # 6 players -> surcharge fires: 400 + 100 = 500
        assert lane_cost("weekday", 1, 6, 0, False) == 500

    def test_max_shoe_rentals_equals_players(self):
        # shoe_rentals == players is valid
        assert lane_cost("weekday", 1, 4, 4, False) == 600

    def test_weekday_example_from_handout(self):
        # given starter test: lane_cost("weekday", 2, 4, 2, False) == 900
        assert lane_cost("weekday", 2, 4, 2, False) == 900


class TestLaneCostErrors:
    """Tests that verify all error-raising statements are reached."""

    def test_unknown_day_type_raises(self):
        with pytest.raises(ValueError, match="unknown day type"):
            lane_cost("holiday", 1, 2, 0, False)

    def test_zero_games_raises(self):
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", 0, 2, 0, False)

    def test_negative_games_raises(self):
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", -1, 2, 0, False)

    def test_zero_players_raises(self):
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", 1, 0, 0, False)

    def test_players_over_6_raises(self):
        with pytest.raises(ValueError, match="invalid booking"):
            lane_cost("weekday", 1, 7, 0, False)

    def test_shoe_rentals_exceed_players_raises(self):
        with pytest.raises(ValueError, match="too many shoe rentals"):
            lane_cost("weekday", 1, 2, 3, False)


# ---------------------------------------------------------------------------
# frame_score tests
# ---------------------------------------------------------------------------

class TestFrameScoreBasic:
    """Happy-path frame scoring – open frame, spare, strike."""

    def test_open_frame_from_handout(self):
        assert frame_score(3, 4, []) == 7

    def test_open_frame_zero_score(self):
        assert frame_score(0, 0, []) == 0

    def test_open_frame_max_pins(self):
        # 4 + 5 = 9 (not a spare or strike)
        assert frame_score(4, 5, []) == 9

    def test_spare(self):
        # 6 + 4 = spare; bonus first roll = 7 → 10 + 7 = 17
        assert frame_score(6, 4, [7, 2]) == 17

    def test_spare_with_zero_bonus(self):
        # bonus first roll = 0 → 10 + 0 = 10
        assert frame_score(7, 3, [0, 5]) == 10

    def test_strike(self):
        # first_roll == 10; bonus = [7, 2] → 10 + 7 + 2 = 19
        assert frame_score(10, 0, [7, 2]) == 19

    def test_strike_perfect(self):
        # bonus = [10, 10] → 30
        assert frame_score(10, 0, [10, 10]) == 30

    def test_strike_bonus_zero(self):
        # bonus = [0, 0] → 10
        assert frame_score(10, 0, [0, 0]) == 10


class TestFrameScoreErrors:
    """Tests that trigger every error-raising statement in frame_score."""

    def test_negative_first_roll_raises(self):
        with pytest.raises(ValueError, match="invalid roll"):
            frame_score(-1, 0, [])

    def test_first_roll_over_10_raises(self):
        with pytest.raises(ValueError, match="invalid roll"):
            frame_score(11, 0, [])

    def test_negative_second_roll_raises(self):
        with pytest.raises(ValueError, match="invalid roll"):
            frame_score(0, -1, [])

    def test_frame_total_over_10_raises(self):
        with pytest.raises(ValueError, match="invalid frame"):
            frame_score(6, 5, [])


# ---------------------------------------------------------------------------
# lane_assignment tests
# ---------------------------------------------------------------------------

class TestLaneAssignment:
    """Covers every return path in lane_assignment."""

    def test_no_free_lanes_returns_wait(self):
        assert lane_assignment(2, False, 0) == "wait"

    def test_has_kids_returns_bumper_lane(self):
        # lanes_free > 0 and has_kids=True
        assert lane_assignment(3, True, 2) == "bumper lane"

    def test_large_group_two_free_lanes(self):
        # players > 6 and lanes_free >= 2
        assert lane_assignment(7, False, 2) == "two lanes"

    def test_large_group_only_one_lane_wait(self):
        # players > 6 but only 1 lane free
        assert lane_assignment(7, False, 1) == "wait"

    def test_standard_group_returns_standard_lane(self):
        # players <= 6, no kids, lanes available
        assert lane_assignment(4, False, 3) == "standard lane"

    def test_boundary_6_players_standard_lane(self):
        # exactly 6 players – should NOT trigger the >6 branch
        assert lane_assignment(6, False, 1) == "standard lane"

    def test_has_kids_overrides_large_group(self):
        # has_kids check comes before the players > 6 check
        assert lane_assignment(8, True, 3) == "bumper lane"

    def test_no_lanes_beats_kids(self):
        # lanes_free == 0 is checked first
        assert lane_assignment(3, True, 0) == "wait"
