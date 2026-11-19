#!/usr/bin/env python3
"""
Achievement 165 - fix the broken whitelabel-calculator links in the 26 localized pages.

What happened:
The bespoke-plan-card / shared-estimator language wave (commit e12c7bc3 and the
parallel waves after it) copied the hero calculator button from the ROOT index.html
into every <lang>/index.html verbatim - keeping the sibling-relative path
  href="./whitelabel-calculator.html"
Inside a language folder that resolves to <lang>/whitelabel-calculator.html, which
does not exist anywhere in the tree: the calculator lives only at the repository
root (whitelabel-calculator.html). The blocking validator therefore fails with
26 "Missing local resource" issues - once for every language except ar/de (which
never received that button) - and both ci.yml and deploy-pages.yml go red.

The fix:
Rewrite the one broken link in each localized page to
  href="../whitelabel-calculator.html"
which is exactly the pattern the rest of the same pages already use for the
calculator (footer links and the platforms card point to ../whitelabel-calculator.html).

Then keep the tracked csp-hashes.txt in sync: build_csp.py hashes the inline
<script> blocks of the built publish set (_site), so the script first rebuilds
_site with prepare_publish_set.py (same order as ci.yml) and only then
regenerates the hashes. Skipping this step fails "build_csp.py --check" in the
next CI run (and some buttons live inside inline JS templates, so the hashes
do change: 6 hash lines moved when the links were fixed).

Safety:
- Idempotent: already-fixed pages are left untouched; re-running is harmless.
- The root index.html is NEVER modified (its ./ link is correct - it lives at the root).
- After fixing: prepare_publish_set.py (build _site) -> build_csp.py (regenerate
  the tracked csp-hashes.txt) -> validate_publish_set.py (the blocking gate),
  printing each verdict so you see PASS immediately.

Usage (from the repository root):
    python scripts/fix_lang_calculator_links.py
"""
from pathlib import Path
import subprocess
import sys

BROKEN = 'href="./whitelabel-calculator.html"'
FIXED = 'href="../whitelabel-calculator.html"'


def run_step(label: str, script: Path, cwd: Path) -> bool:
    print(f"\n--- {label} ---")
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(cwd),
        text=True,
        capture_output=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = [ln for ln in out.strip().splitlines() if ln.strip()][-4:]
    for ln in tail:
        print("  |", ln)
    if proc.returncode == 0:
        print("  RESULT: PASS")
        return True
    print(f"  RESULT: FAIL (rc={proc.returncode})")
    return False


def main() -> int:
    # Locate the repository root: prefer CWD if it looks like the repo, else
    # assume this script lives in <repo>/scripts/.
    root = Path.cwd()
    if not (root / "scripts" / "validate_publish_set.py").exists():
        root = Path(__file__).resolve().parent.parent
    if not (root / "scripts" / "validate_publish_set.py").exists():
        print("ERROR: could not find the repository root.")
        print("Run from the repository root:  python scripts/fix_lang_calculator_links.py")
        return 1
    print(f"repository root: {root}")

    changed, skipped = 0, 0
    for page in sorted(root.glob("*/index.html")):
        text = page.read_text(encoding="utf-8")
        n = text.count(BROKEN)
        if not n:
            if FIXED in text:
                skipped += 1
            continue
        page.write_text(text.replace(BROKEN, FIXED), encoding="utf-8")
        changed += 1
        print(f"fixed    {page.relative_to(root)} : {n} link(s)  ./ -> ../")

    if changed == 0 and skipped > 0:
        print("nothing to fix - every localized page already points to ../whitelabel-calculator.html")
    print(f"\npages rewritten: {changed}   already correct: {skipped}")

    ok_bld = run_step("build publish set (prepare_publish_set.py)", root / "scripts" / "prepare_publish_set.py", root)
    ok_csp = run_step("regenerate csp-hashes.txt (build_csp.py)", root / "scripts" / "build_csp.py", root)
    ok_val = run_step("blocking gate: validate_publish_set.py", root / "scripts" / "validate_publish_set.py", root)

    if ok_val:
        if changed == 0 and skipped > 0:
            print("\nALL GREEN - commit csp-hashes.txt only if it changed; otherwise nothing to commit.")
        else:
            print("\nALL GREEN - now commit the modified pages together with csp-hashes.txt and push.")
        return 0
    print("\nValidator still failing - paste its full output as-is (error protocol: no experiments).")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
