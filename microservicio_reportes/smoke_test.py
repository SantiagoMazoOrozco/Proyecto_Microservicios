import requests
import time
import os

BASE = 'http://127.0.0.1:5002'

resp = requests.post(BASE + '/reports', json={'title': 'Prueba rapida'})
print('POST /reports ->', resp.status_code, resp.text)
if resp.status_code not in (200, 202):
    raise SystemExit('Create failed')

data = resp.json()
report_id = data.get('id')
if not report_id:
    raise SystemExit('No id returned')

print('Created id=', report_id)

for i in range(20):
    r = requests.get(f"{BASE}/reports/{report_id}/status")
    if r.status_code != 200:
        print('Status fetch failed', r.status_code, r.text)
        break
    meta = r.json().get('meta')
    print('Attempt', i, 'meta=', meta)
    status = meta.get('status') if isinstance(meta, dict) else None
    if status == 'ready':
        out_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(out_dir, exist_ok=True)
        # try pdf first
        out_path = os.path.join(out_dir, report_id + '.pdf')
        dl = requests.get(f"{BASE}/reports/{report_id}/download")
        if dl.status_code == 200:
            with open(out_path, 'wb') as f:
                f.write(dl.content)
            print('Saved to', out_path)
            break
        else:
            print('Download failed', dl.status_code)
    time.sleep(1)
print('Done')
