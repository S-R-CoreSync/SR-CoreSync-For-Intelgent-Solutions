import urllib.request, json
url = 'https://api.github.com/repos/S-R-CoreSync/SR-CoreSync-For-Intelgent-Solutions/actions/runs/43620669900/jobs'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        for job in data.get('jobs', []):
            print(f"{job['name']}: {job['status']} - {job['conclusion']}")
            for step in job.get('steps', []):
                if step.get('conclusion') == 'failure':
                    print(f"  Step failed: {step['name']}")
except Exception as e:
    print('Error:', e)
