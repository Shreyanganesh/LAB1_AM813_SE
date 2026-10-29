# Lab 6 – Code and Branch Coverage Analysis

**Student ID:** PES1UG25AM813  
**Subject:** Software Engineering (AM813)  
**Lab:** 6 – Code Coverage and Branch Coverage  

---

## Objective

Achieve **≥ 90% code (statement) coverage** and **≥ 90% branch coverage** for the assigned application using Python, `pytest`, and the `coverage` library.

---

## Application Analysed

**`bowling_alley.py`** — A small Python module with three public functions:

| Function | Description |
|---|---|
| `lane_cost(day_type, games, players, shoe_rentals, is_league_member)` | Calculates the total cost for a lane booking, applying player surcharges and league-member discounts. |
| `frame_score(first_roll, second_roll, bonus_rolls)` | Scores a single bowling frame handling open frames, spares, and strikes. |
| `lane_assignment(players, has_kids, lanes_free)` | Assigns a party to a lane (bumper, two-lane, standard, or wait). |

---

## Repository Structure

```
lab6/
├── bowling_alley.py                                    # Application under test (unchanged)
├── CodeCoverageTest_PES1UG25AM813_bowling_alley.py     # Code coverage test suite (40 tests)
├── BranchCoverageTest_PES1UG25AM813_bowling_alley.py  # Branch coverage test suite (44 tests)
├── code_coverage_terminal_output.txt                   # Terminal output – code coverage run
├── branch_coverage_terminal_output.txt                 # Terminal output – branch coverage run
├── .coveragerc                                         # Coverage configuration
└── README.md                                           # This file
```

---

## Environment Setup

```bash
pip install pytest pytest-cov coverage
```

- Python 3.13.9
- pytest 8.4.2
- coverage 7.17.0
- pytest-cov 7.1.0

---

## Execution Commands

### Code Coverage (Statement Coverage)

```bash
cd lab6
coverage run --source=bowling_alley -m pytest CodeCoverageTest_PES1UG25AM813_bowling_alley.py -v
coverage report -m
```

### Branch Coverage

```bash
cd lab6
coverage run --source=bowling_alley --branch -m pytest BranchCoverageTest_PES1UG25AM813_bowling_alley.py -v
coverage report -m
```

---

## Coverage Analysis

### Code Coverage (`bowling_alley.py`)

| Metric | Value |
|---|---|
| Statements | 35 |
| Statements missed | 0 |
| **Code Coverage** | **100%** |

Every statement in the module is exercised by the 40 tests in `CodeCoverageTest_PES1UG25AM813_bowling_alley.py`.

### Branch Coverage (`bowling_alley.py`)

| Metric | Value |
|---|---|
| Branches | 26 |
| Partial branches | 0 |
| **Branch Coverage** | **100%** |

Every True/False outcome of every conditional in the module is exercised by the 44 tests in `BranchCoverageTest_PES1UG25AM813_bowling_alley.py`.

---

## Branch Map

### `lane_cost`

| ID | Condition | True → | False → |
|---|---|---|---|
| B1 | `day_type not in LANE_RATE` | raise ValueError | continue |
| B2 | `games < 1 or players < 1 or players > 6` | raise ValueError | continue |
| B3 | `shoe_rentals > players` | raise ValueError | continue |
| B4 | `players > 4` | add surcharge | skip surcharge |
| B5 | `is_league_member` | apply discount | skip discount |

### `frame_score`

| ID | Condition | True → | False → |
|---|---|---|---|
| B6 | `first_roll < 0` | raise ValueError | continue |
| B7 | `first_roll > 10` | raise ValueError | continue |
| B8 | `second_roll < 0` | raise ValueError | continue |
| B9 | `first_roll == 10` (strike) | return 10+bonus[0]+bonus[1] | continue |
| B10 | `first+second > 10` | raise ValueError | continue |
| B11 | `first+second == 10` (spare) | return 10+bonus[0] | return sum |

### `lane_assignment`

| ID | Condition | True → | False → |
|---|---|---|---|
| B12 | `lanes_free == 0` | return "wait" | continue |
| B13 | `has_kids` | return "bumper lane" | continue |
| B14 | `players > 6 and lanes_free >= 2` | return "two lanes" | continue |
| B15 | `players > 6` (elif) | return "wait" | return "standard lane" |

---

## Actual Results

### Code Coverage Run
```
40 passed in 0.04s

Name               Stmts   Miss  Cover   Missing
------------------------------------------------
bowling_alley.py      35      0   100%
------------------------------------------------
TOTAL                 35      0   100%
```

### Branch Coverage Run
```
44 passed in 0.05s

Name               Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------
bowling_alley.py      35      0     26      0   100%
--------------------------------------------------------------
TOTAL                 35      0     26      0   100%
```

---

## Deliverables

| # | File | Description |
|---|---|---|
| 1 | `CodeCoverageTest_PES1UG25AM813_bowling_alley.py` | 40 tests achieving 100% code coverage |
| 2 | `BranchCoverageTest_PES1UG25AM813_bowling_alley.py` | 44 tests achieving 100% branch coverage |
| 3 | `code_coverage_terminal_output.txt` | Terminal output from code coverage run |
| 4 | `branch_coverage_terminal_output.txt` | Terminal output from branch coverage run |
| 5 | `bowling_alley.py` | Original application (unmodified) |
| 6 | `.coveragerc` | Coverage configuration |
| 7 | `README.md` | This documentation |
