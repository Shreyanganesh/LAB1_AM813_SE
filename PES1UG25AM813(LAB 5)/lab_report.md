# Lab 5 Report — Static Code Analysis
## Public Transit Fare Calculator

**Student ID:** PES1UG25AM813  
**Date:** 27 October 2026  
**Duration:** 60 minutes  
**Tools Used:** Pylint, Flake8, Bandit  

---

## 1. Initial Analysis Results (Before Fixes)

### Pylint — Score: 5.80 / 10
| Code | Message | Lines |
|------|---------|-------|
| C0114 | Missing module docstring | 1 |
| C3001 / W0108 | Lambda assigned to variable / unnecessary lambda | 14 |
| C0116 | Missing function docstrings | 16,23,27,35,43,46,52,56,59,73,78,85 |
| C0103 | Non-snake_case function names | 16,23,27,35,43,46,52,56,59,73,78 |
| W0120 | Useless else on loop | 20 |
| R1728 / R1721 | Unnecessary sum comprehension | 37 |
| R1730 | Use min() instead of if block | 39 |
| W0102 | Dangerous mutable default argument | 46 |
| W0108 | Unnecessary lambda in sorted() | 57 |
| C0115 | Missing class docstring | 64 |
| W0611 | Unused import `os` | 1 |

### Bandit — 5 Issues Found
| Check | Severity | Line | Description |
|-------|----------|------|-------------|
| B406 | Low | 2 | `import xml.sax` — use defusedxml |
| B303 | **Medium** | 60 | MD5 hash — insecure |
| B317 | **Medium** | 75 | `xml.sax.parseString` — XML injection |
| B507 | **High** | 80 | Paramiko AutoAddPolicy — MITM risk |
| B601 | **Medium** | 82 | Paramiko exec_command — shell injection |

### Flake8 — 20 Issues Found
| Code | Count | Description |
|------|-------|-------------|
| F401 | 1 | `os` imported but unused |
| E731 | 1 | Lambda assignment (use def) |
| E302 | 13 | Missing two blank lines |
| E501 | 4 | Lines exceeding 79 characters |
| E305 | 1 | Missing blank lines after last function |

---

## 2. Fixes Applied

### Fix Set 1 — Security Issues (Bandit)
1. **MD5 → SHA-256**: Replaced `hashes.Hash(hashes.MD5())` with `hashlib.sha256()` (B303).
2. **XML safety**: Replaced `xml.sax.parseString` with `defusedxml.sax.parseString` and called `defusedxml.defuse_stdlib()` at startup (B317 / B406).
3. **SSH host-key verification**: Replaced `AutoAddPolicy()` with `load_system_host_keys()` + `RejectPolicy()` (B507).
4. **Shell injection prevention**: Applied `shlex.quote()` to the `fare_file` argument before concatenation (B601).

### Fix Set 2 — Code Quality (Pylint)
5. Removed unused `import os` (W0611).
6. Deleted `baseOf` lambda; call sites use `fare_for_distance` directly (C3001 / W0108).
7. Changed `categories=[]` to `categories=None` with body initialisation (W0102).
8. Fixed useless `else` on `for` loop in `fare_for_distance` (W0120).
9. Fixed broken daily-cap logic: cap now applied via `min(f, DAILY_CAP)` in list comprehension (R1730 / logic bug).
10. Renamed all camelCase functions to snake_case (C0103).
11. Added module, class, and function docstrings throughout (C0114 / C0115 / C0116).
12. Removed unnecessary lambda from `sorted()` call (W0108).

### Fix Set 3 — Style (Flake8)
13. Added required blank lines between all top-level definitions (E302 / E305).
14. Wrapped long lines using implicit parenthetical continuation (E501).

---

## 3. After Analysis Results

### Pylint — Score: **10.00 / 10** ✅
No issues reported.

### Bandit — **No issues identified** ✅
- Total issues (Low/Medium/High): 0 / 0 / 0
- 2 items suppressed with `# nosec` annotations (documented with rationale).

### Flake8 — **No issues reported** ✅
Zero violations. Clean exit code 0.

---

## 4. Logical Bug Fixed (Not Flagged by Tools)

The daily-cap loop was **silently broken**:

```python
# BEFORE — cap never applied; f is a local loop variable
for f in fares:
    if f > DAILY_CAP:
        f = DAILY_CAP   # reassigns local var, original list unchanged
return total            # total already computed from un-capped fares!
```

```python
# AFTER — cap applied correctly before summing
capped = [min(f, DAILY_CAP) for f in fares]
return sum(capped)
```

This bug would result in **financial overcharging** of commuters beyond the advertised daily cap.

---

## 5. Summary Table

| Category | Before | After |
|----------|--------|-------|
| Pylint score | 5.80 / 10 | **10.00 / 10** |
| Bandit High | 1 | **0** |
| Bandit Medium | 3 | **0** |
| Bandit Low | 1 | **0** |
| Flake8 violations | 20 | **0** |
| Pylint messages | 34 | **0** |
