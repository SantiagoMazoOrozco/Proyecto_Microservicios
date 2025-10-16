import os
import json
from flask import Flask, request, jsonify, send_file
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv
from storage import local_path_for_report, report_meta_path, read_meta, write_meta

load_dotenv()

app = Flask(__name__)
REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Simple in-memory start time for uptime
START_TIME = datetime.utcnow()


@app.route('/health', methods=['GET'])
def health():
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    return jsonify({'status': 'ok', 'uptime_seconds': int(uptime)})


@app.route('/reports', methods=['POST'])
def create_report():
    payload = request.json or {}
    report_id = str(uuid4())
    meta = {
        'id': report_id,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat(),
        'type': payload.get('type','pdf')
    }
    # write meta as JSON
    write_meta(report_id, meta)

    # enqueue task; if Celery or Redis not available, fallback to sync generation so tests can run locally
    try:
        from tasks import generate_report_async
        # prefer async if available
        if hasattr(generate_report_async, 'delay'):
            generate_report_async.delay(report_id, payload)
        else:
            # not a celery task, call sync function
            from tasks import generate_report
            generate_report(report_id, payload)
    except Exception:
        # fallback: try synchronous generation in-process (useful for local dev without Redis)
        try:
            from tasks import generate_report
            generate_report(report_id, payload)
        except Exception as exc:
            # final fallback: mark error in meta
            meta = {'id': report_id, 'status': 'error', 'error': str(exc)}
            write_meta(report_id, meta)
            print('Error generating report synchronously:', exc)

    return jsonify({'id': report_id, 'status': 'pending'}), 202


@app.route('/reports/<report_id>/status', methods=['GET'])
def status(report_id):
    meta = read_meta(report_id)
    if meta is None:
        return jsonify({'message':'not found'}), 404
    return jsonify({'id': report_id, 'meta': meta})


@app.route('/reports/<report_id>/download', methods=['GET'])
def download(report_id):
    path = local_path_for_report(report_id)
    if not os.path.exists(path):
        return jsonify({'message':'not ready'}), 404
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5002))
    app.run(host='0.0.0.0', port=port)
