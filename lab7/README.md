# Lab 7 – Fuzz Testing with Hypothesis

**Student:** Shreyang A Ganesh  
**SRN:** PES1UG25AM813  
**Course:** Software Engineering  
**University:** PES University

---

## About

This lab applies property-based fuzz testing using **Hypothesis** to a bowling alley parser module (`processor.py`) that reads player names, bowling frame notations, and scoreboards from user input. The original code assumes all inputs are well-formed and crashes on anything unexpected.

Hypothesis automatically generates thousands of random, edge-case, and malformed inputs to expose hidden bugs that manual testing would miss.

## Files

| File | Description |
|------|-------------|
| `processor.py` | Bowling alley parser — fixed with defensive input validation |
| `test_processor.py` | 12 Hypothesis fuzz tests covering all three functions |
| `requirements.txt` | Python dependencies (hypothesis, pytest) |
| `screenshots/01_original_output.png` | Original app execution with valid inputs |
| `screenshots/02_failing_tests.png` | Fuzz tests failing on the buggy module (6 failures) |
| `screenshots/03_fixed_output.png` | Fixed app execution with valid inputs |
| `screenshots/04_passing_tests.png` | All 12 fuzz tests passing on the fixed module |
| `reports/Lab7_FuzzTesting_Report.pdf` | Lab report with screenshots and analysis |

## Three Functions Tested

1. **`format_player_name(name)`** — Title-cases a player name and truncates to 10 characters.
2. **`parse_frame(text)`** — Parses bowling frame notation (`X`, `7/`, `45`) into pin counts.
3. **`parse_scoreboard(text)`** — Parses `Name:Score,Name:Score` into a dictionary.

## Bugs Discovered by Fuzzing

| Bug | Function | Input | Error |
|-----|----------|-------|-------|
| 1 | `format_player_name` | `None` | `AttributeError: 'NoneType' has no attribute 'strip'` |
| 2 | `parse_frame` | `None` | `AttributeError: 'NoneType' has no attribute 'strip'` |
| 3 | `parse_frame` | `""` (empty) | `IndexError: string index out of range` |
| 4 | `parse_frame` | `":"` (non-digit) | `ValueError: invalid literal for int()` |
| 5 | `parse_frame` | `"0"` (single char) | `IndexError: string index out of range` |
| 6 | `parse_scoreboard` | `None` | `AttributeError: 'NoneType' has no attribute 'split'` |
| 7 | `parse_scoreboard` | `""` (empty) | `ValueError: not enough values to unpack` |
| 8 | `parse_scoreboard` | `":"` (empty score) | `ValueError: invalid literal for int()` |

## Fixes Applied

All fixes use **defensive programming** — validate inputs before processing, return safe defaults for invalid data, and use try/except for parsing operations.

- **`format_player_name`**: Added `isinstance(name, str)` check; returns `""` for None or empty.
- **`parse_frame`**: Added type check, length validation, and `try/except ValueError` around `int()` calls; returns `(0, 0)` for invalid input.
- **`parse_scoreboard`**: Added type check, `:` presence validation, and `try/except ValueError` around `int()` for scores; skips malformed entries and returns `{}` for invalid input.

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python processor.py

# Run fuzz tests
pytest test_processor.py -v
```

## Test Results

- **Before fix:** 6 failed, 6 passed (12 total)
- **After fix:** 12 passed, 0 failed
