# -*- coding: utf-8 -*-
"""Run the deploy job's commands in order, printing each exit code, in a clean clone."""
import os, shutil, subprocess, sys, tempfile

SRC = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
tmp = tempfile.mkdtemp(prefix='sr-ci-')
dst = os.path.join(tmp, 'repo')
subprocess.run(['git', 'clone', '--quiet', SRC, dst], check=True)
print('clone:', dst)

STEPS = [
    ('build pages', [['python', 'scripts/build_site.py', '--build'],
                     ['python', 'scripts/build_lang.py', '--build', 'en']]),
    ('verify pages', [['python', 'scripts/build_site.py', '--check'],
                      ['python', 'scripts/build_lang.py', '--check', 'en'],
                      ['python', 'scripts/check_hreflang.py'],
                      ['python', 'scripts/check_sr_args.py']]),
    ('build publish set', [['python', 'scripts/prepare_publish_set.py']]),
    ('verify integrity', [['python', 'scripts/validate_publish_set.py'],
                          ['python', 'scripts/check_site_links.py']]),
]

for label, cmds in STEPS:
    for cmd in cmds:
        p = subprocess.run(cmd, cwd=dst, capture_output=True, text=True, errors='replace')
        ok = 'ok' if p.returncode == 0 else 'FAIL(%d)' % p.returncode
        print('%-22s %-46s %s' % (label, ' '.join(cmd[1:]), ok))
        if p.returncode != 0:
            tail = (p.stdout + p.stderr).strip().splitlines()[-6:]
            for line in tail:
                print('      ', line)
