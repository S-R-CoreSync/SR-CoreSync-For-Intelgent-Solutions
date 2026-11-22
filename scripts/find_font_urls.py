import os, re

root = os.getcwd()
urls = set()
files_with_gf = []

for dirpath, dirs, files in os.walk(root):
    if any(x in dirpath for x in ['_site', '.venv', 'node_modules', '.git', 'scratch']):
        continue
    for f in files:
        if not f.endswith(('.html', '.css', '.js')):
            continue
        p = os.path.join(dirpath, f)
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
                matches = re.findall(r'https://fonts\.googleapis\.com/css2\?[^\'"\s<>]+', content)
                if matches:
                    rel = os.path.relpath(p, root)
                    files_with_gf.append((rel, len(matches)))
                    for m in matches:
                        urls.add(m)
        except Exception:
            pass

print(f"Files referencing Google Fonts: {len(files_with_gf)}")
print(f"Distinct Google Fonts stylesheets: {len(urls)}")
for u in sorted(urls):
    print(" -", u)
