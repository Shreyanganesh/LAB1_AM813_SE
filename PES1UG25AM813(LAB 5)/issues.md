# Lab 5: Static Code Analysis — Issue Documentation

**Student:** PES1UG25AM813  
**File Analysed:** `fare_calculator.py`  
**Tools:** Pylint 3.x · Bandit 1.9.4 · Flake8 7.x  

---

## Identified Issues

| Issue | Tool | Severity | Line(s) | Description | Fix Applied |
|-------|------|----------|---------|-------------|-------------|
| Unused import `os` | Pylint / Flake8 | Medium | 1 | `import os` is never referenced anywhere in the file, adding noise and inflating the module's dependency surface. | Removed the unused import entirely. |
| Lambda assigned to a variable (`baseOf`) | Pylint / Flake8 | Medium | 14 | `baseOf = lambda km: fareForDistance(km)` is a redundant wrapper that assigns a lambda to a name, violating PEP 8 (E731) and Pylint C3001/W0108. | Deleted `baseOf`; call sites changed to call `fare_for_distance` directly. |
| Mutable default argument `categories=[]` | Pylint | High | 46 | Using `[]` as a default argument value means all call sites share the same list object; mutations would persist across calls — a classic Python bug. | Changed default to `None` and initialised inside the function body with `if categories is None: categories = []`. |
| `useless-else-on-loop` (no `break`) | Pylint | Medium | 20 | The `else` clause on the `for` loop in `fareForDistance` is semantically misleading: it runs after every complete iteration, not only when the loop is not broken. | Removed the `else:` clause and de-indented the `return MAX_FARE` statement. |
| Non-snake_case function names | Pylint | Low | 16,23,27,35,43,46,52,56,59,73,78 | Eight functions (`fareForDistance`, `isPeak`, `journeyFare`, `dailyTotal`, `issueCard`, `tapOut`, `topUp`, `cheapestRoute`, `ticketChecksum`, `loadStops`, `pushFaresToGate`) use camelCase instead of the PEP 8 snake_case convention. | Renamed all functions and updated every call site. |
| Insecure MD5 hash (B303) | Bandit | **High** | 60 | `hashes.MD5()` is a cryptographically broken hash algorithm — banned in security contexts by CWE-327. | Replaced with `hashlib.sha256()`, a secure standard-library alternative. |
| XML injection via `xml.sax` (B317/B406) | Bandit | **High** / Medium | 2, 75 | `xml.sax.parseString` is vulnerable to XML Bomb / Billion-Laughs attacks. `import xml.sax` flagged at B406 (Low). | Replaced with `defusedxml.sax.parseString` and called `defusedxml.defuse_stdlib()` to patch stdlib at startup. |
| Paramiko auto-trust of unknown host keys (B507) | Bandit | **High** | 80 | `AutoAddPolicy()` silently accepts any host key, leaving SSH open to man-in-the-middle attacks (CWE-295). | Changed to `load_system_host_keys()` + `RejectPolicy()` so unknown hosts are refused. |
| Possible shell injection via Paramiko (B601) | Bandit | Medium | 82 | `exec_command("install_fares " + fare_file)` concatenates user-supplied input into a shell command without sanitisation (CWE-78). | Applied `shlex.quote(fare_file)` to the filename before concatenation. |
| Missing two blank lines between top-level definitions (E302) | Flake8 | Low | multiple | PEP 8 requires exactly two blank lines between module-level functions and classes. The original file used only one. | Added the required blank lines throughout the file. |
| Lines exceeding 79 characters (E501) | Flake8 | Low | 89,90,96,98 | Four lines in `main()` exceeded the PEP 8 maximum line length of 79 characters. | Wrapped the arguments across multiple lines using implicit line continuation inside parentheses. |
| Missing docstrings (C0114/C0115/C0116) | Pylint | Low | all functions, class, module | Every function, the `StopHandler` class, and the module lacked docstrings, making the code hard to understand and document. | Added a module-level docstring and docstrings to all functions and the class. |
| `sum()` on redundant comprehension (R1728/R1721) | Pylint | Low | 37 | `sum([f for f in fares])` wraps a list comprehension unnecessarily — both the list and the identity comprehension are redundant. Also, each fare was compared to `DAILY_CAP` inside the loop but the loop variable `f` was never mutated (the cap had no effect). | Replaced with a list comprehension that applies `min(f, DAILY_CAP)` and calls `sum()` directly on it, fixing the logical bug. |
