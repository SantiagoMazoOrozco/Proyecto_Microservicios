import os
import json
from dotenv import load_dotenv

load_dotenv()
REPORTS_DIR = os.getenv('REPORTS_DIR','reports')
os.makedirs(REPORTS_DIR, exist_ok=True)


def local_path_for_report(report_id):
    return os.path.join(REPORTS_DIR, f"{report_id}.pdf")


def report_meta_path(report_id):
    return os.path.join(REPORTS_DIR, f"{report_id}.meta.json")


def write_meta(report_id, data):
    path = report_meta_path(report_id)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_meta(report_id):
    path = report_meta_path(report_id)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_presigned_url(report_id):
    # placeholder for S3; for local returns download endpoint
    return f"/reports/{report_id}/download"
