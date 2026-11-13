import sys, os, difflib, re, importlib.util
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
spec = importlib.util.spec_from_file_location('sl', os.path.join(ROOT, 'scripts', 'sync_locales.py'))
sl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sl)

lang = sys.argv[1] if len(sys.argv) > 1 else 'de'
hero_tpl, css_tpl = sl.master_parts()
table = sl.load_locale(lang) if hasattr(sl, 'load_locale') else __import__('json').load(open(os.path.join(ROOT, 'i18n', 'locales', lang + '.json'), encoding='utf-8'))
head, css = sl.render(hero_tpl, css_tpl, table)

cur = sl.read(os.path.join(ROOT, lang, 'index.html'))
nl = '\r\n' if '\r\n' in cur else '\n'
exp = cur
a = exp.index(sl.BEGIN) + len(sl.BEGIN); b = exp.index(sl.END)
exp = exp[:a] + nl + head + nl + exp[b:]
m = re.search(r'(<style id="hv2-port">)(.*?)(</style>)', exp, re.S)
exp = exp[:m.start(2)] + nl + css + nl + exp[m.end(2):]

d = list(difflib.unified_diff(cur.splitlines(), exp.splitlines(), 'current', 'expected', n=1, lineterm=''))
print('\n'.join(d[:30]) if d else 'no difference')
print('changed lines:', len([x for x in d if x[:1] in '+-' and not x.startswith(('+++', '---'))]))
