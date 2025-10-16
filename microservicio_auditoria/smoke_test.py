import requests
import time
import os

BASE = os.getenv('AUDIT_BASE', 'http://127.0.0.1:5003')

def main():
    print('Checking health...')
    try:
        r = requests.get(BASE + '/health', timeout=3)
        print('health', r.status_code, r.text)
    except Exception as e:
        print('Health check failed:', e)
        return

    # create a log
    payload = {
        'level': 'INFO',
        'service': 'smoke-test',
        'message': 'mensaje de prueba desde smoke_test',
        'meta': {'attempt': 1}
    }
    try:
        r = requests.post(BASE + '/logs', json=payload, timeout=5)
        print('POST /logs ->', r.status_code, r.text)
    except Exception as e:
        print('POST /logs failed:', e)
        return

    # query back
    time.sleep(0.5)
    try:
        r = requests.get(BASE + '/search', params={'q': 'prueba', 'page': 1, 'size': 5}, timeout=5)
        print('GET /search ->', r.status_code)
        print(r.text)
    except Exception as e:
        print('Search failed:', e)

if __name__ == '__main__':
    main()
