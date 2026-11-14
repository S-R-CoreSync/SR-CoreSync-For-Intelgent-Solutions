import urllib.request, json
url = 'https://api.github.com/repos/S-R-CoreSync/SR-CoreSync-For-Intelgent-Solutions/actions/runs'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print('Total workflow runs:', data.get('total_count', 0))
        for run in data.get('workflow_runs', [])[:5]:
            print(f"{run['id']}: {run['name']} - {run['status']} - {run['conclusion']} - commit: {run['head_sha'][:8]}")
except Exception as e:
    print('Error:', e)
