import urllib.request, json
url = 'https://api.github.com/repos/S-R-CoreSync/SR-CoreSync-For-Intelgent-Solutions/actions/runs?per_page=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        for r in data.get('workflow_runs', []):
            print(f"{r['id']}: {r['name']} - {r['status']} - {r['conclusion']} - {r['updated_at']}")
except Exception as e:
    print('Error:', e)
