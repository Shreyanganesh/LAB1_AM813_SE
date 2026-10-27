# Lab 5: Static Code Analysis — Reflection

**Student:** PES1UG25AM813  
**Date:** 27 October 2026  

---

## Reflection Questions

### Q1. What is static code analysis, and why is it important in software development?

Static code analysis is the process of examining source code **without executing it** in order to detect bugs, style violations, security vulnerabilities, and maintainability problems. Unlike runtime testing, it covers every code path — including those rarely triggered by test inputs — and catches whole classes of defect before they reach production.

It matters because:

- **Security** – tools like Bandit flag dangerous patterns (e.g., insecure hashing, shell injection) that might otherwise survive peer review.
- **Consistency** – style linters such as Flake8 enforce a shared coding standard, making the codebase easier to read across a team.
- **Quality** – quality analysers such as Pylint detect logical pitfalls (mutable default arguments, useless else-on-loop, unused imports) that silently corrupt program behaviour.
- **Cost** – finding defects statically is far cheaper than hunting them in production incidents.

---

### Q2. Which tool — Pylint, Flake8, or Bandit — did you find most useful, and why?

**Bandit** was the most impactful for this codebase. The original code contained five genuine security vulnerabilities: MD5 hashing, XML injection via `xml.sax`, SSH host-key auto-trust, and potential shell injection. None of these would have been caught by a style linter, and all of them could cause serious harm in a production system.

Pylint came a close second: it found the mutable default argument (`categories=[]`) and the broken daily-cap logic (the `for` loop modified a local copy of `f` rather than the list entry, so the cap never applied) — both logic bugs with real-world consequences for fare charging.

Flake8 was the most mechanical but still useful for enforcing the spacing and line-length rules that make code readable.

---

### Q3. Describe one bug or issue that surprised you. What was its impact?

The **daily cap not being applied** (line 38–40 in the original) was the most surprising bug. The original code was:

```python
for f in fares:
    if f > DAILY_CAP:
        f = DAILY_CAP
```

In Python, assigning to the loop variable `f` does **not** modify the original list. The `total` was therefore computed from un-capped fares, meaning commuters with very long journeys could be overcharged beyond the advertised daily cap — a direct financial harm to customers.

The fix was to apply the cap during the list comprehension itself:

```python
capped = [min(f, DAILY_CAP) for f in fares]
return sum(capped)
```

This also simplified the code and was the pattern Pylint suggested via the `consider-using-min-builtin` hint.

---

### Q4. How will you incorporate static analysis into your future development workflow?

Going forward I will:

1. **Run tools on every commit** by adding Pylint, Flake8, and Bandit as pre-commit hooks (via the `pre-commit` framework) or as steps in a CI pipeline (GitHub Actions / GitLab CI). No code that fails analysis should merge to the main branch.

2. **Triage by severity** – High Bandit findings and Pylint errors are blockers; Low Pylint/Flake8 messages are fixed in a dedicated style pass rather than mixed into feature commits.

3. **Treat new warnings as regressions** – configure tools to fail the build if the score drops compared with the previous run, so quality only ever improves.

4. **Document suppressions** – any `# nosec` or `# noqa` annotation must include a brief rationale (e.g., `# nosec B601 – input validated by shlex.quote`) so future reviewers understand the conscious trade-off.

5. **Pair static analysis with unit tests** – static tools find structural and security problems; tests verify behavioural correctness. Both are necessary, neither is sufficient alone.
