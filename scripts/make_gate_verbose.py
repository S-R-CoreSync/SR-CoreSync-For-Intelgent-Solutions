"""Make the publish-set gate say why it failed, in a form the API can read.

A step that exits 1 without a message costs an hour of guessing. Every failure
line is now emitted as a GitHub annotation, which survives in the run record.
"""
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\.github\workflows\deploy-pages.yml'
s = open(P, encoding='utf-8', newline='').read()

old = """      - name: Verify publish set integrity (no broken local references)
        run: |
          set -euo pipefail
          python scripts/validate_publish_set.py
          python scripts/check_site_links.py"""

new = """      - name: Verify publish set integrity (no broken local references)
        run: |
          set -uo pipefail
          rc=0
          for step in "scripts/validate_publish_set.py" "scripts/check_site_links.py"; do
            out=$(python "$step" 2>&1) || rc=1
            if [ $? -ne 0 ]; then :; fi
            echo "$out"
            if ! echo "$out" | grep -q "PASSED"; then
              rc=1
              echo "::error::FAILED $step"
              echo "$out" | tail -n 25 | sed 's/^/::error::/'
            fi
          done
          exit $rc"""

assert old in s, 'anchor changed'
s = s.replace(old, new, 1)
open(P, 'w', encoding='utf-8', newline='').write(s)
print('gate now reports its own failure')
