import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from datetime import datetime
from pymongo import MongoClient, ASCENDING, TEXT
from dotenv import load_dotenv
import requests

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'audit_db')
COL_NAME = os.getenv('COL_NAME', 'logs')
SECURITY_SERVICE_URL = os.getenv('SECURITY_SERVICE_URL', '')
PORT = int(os.getenv('PORT', 5003))

app = Flask(__name__)
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
col = db[COL_NAME]


def ensure_indexes():
    try:
        col.create_index([('timestamp', ASCENDING)])
        col.create_index([('level', ASCENDING)])
        col.create_index([('service', ASCENDING)])
        col.create_index([('message', TEXT)], default_language='english')
    except Exception:
        pass


class LogItem(BaseModel):
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    level: str
    service: str
    message: str
    meta: Optional[dict] = {}


def validate_token_from_header():
    if not SECURITY_SERVICE_URL:
        return True
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return False
    token = auth.split(' ', 1)[1]
    try:
        r = requests.post(f"{SECURITY_SERVICE_URL}/api/token/validate", json={'token': token}, timeout=2)
        return r.status_code == 200
    except Exception:
        return False


ensure_indexes()


@app.route('/health', methods=['GET'])
def health():
    try:
        client.admin.command('ping')
        return jsonify({'status': 'ok', 'storage': 'mongo', 'db': DB_NAME}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500


@app.route('/logs', methods=['POST'])
def create_log():
    if not validate_token_from_header():
        return jsonify({'detail': 'invalid_token'}), 403
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({'detail': 'invalid_json'}), 422
    try:
        item = LogItem.parse_obj(payload)
    except ValidationError as ve:
        return jsonify({'detail': ve.errors()}), 422
    doc = item.dict()
    res = col.insert_one(doc)
    return jsonify({'id': str(res.inserted_id)}), 201


@app.route('/logs/bulk', methods=['POST'])
def bulk_logs():
    if not validate_token_from_header():
        return jsonify({'detail': 'invalid_token'}), 403
    payload = request.get_json(force=True, silent=True)
    if not isinstance(payload, list):
        return jsonify({'detail': 'expecting array'}), 422
    docs = []
    errors = []
    for i, p in enumerate(payload):
        try:
            item = LogItem.parse_obj(p)
            docs.append(item.dict())
        except ValidationError as ve:
            errors.append({'index': i, 'errors': ve.errors()})
    if errors:
        return jsonify({'detail': 'validation_failed', 'errors': errors}), 422
    if docs:
        col.insert_many(docs)
    return jsonify({'inserted': len(docs)}), 202


@app.route('/search', methods=['GET'])
def search():
    q = {}
    start = request.args.get('start')
    end = request.args.get('end')
    level = request.args.get('level')
    service = request.args.get('service')
    text = request.args.get('q')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 50))
    if start or end:
        tsq = {}
        if start:
            try:
                tsq['$gte'] = datetime.fromisoformat(start)
            except Exception:
                return jsonify({'detail': 'bad start datetime'}), 422
        if end:
            try:
                tsq['$lte'] = datetime.fromisoformat(end)
            except Exception:
                return jsonify({'detail': 'bad end datetime'}), 422
        q['timestamp'] = tsq
    if level:
        q['level'] = level
    if service:
        q['service'] = service
    if text:
        q['$text'] = {'$search': text}
    cursor = col.find(q).sort('timestamp', -1).skip((page-1)*size).limit(size)
    results = []
    for d in cursor:
        d['id'] = str(d['_id'])
        d.pop('_id', None)
        if isinstance(d.get('timestamp'), datetime):
            d['timestamp'] = d['timestamp'].isoformat()
        results.append(d)
    total = col.count_documents(q)
    return jsonify({'total': total, 'page': page, 'size': size, 'items': results}), 200


@app.route('/stats', methods=['GET'])
def stats():
    try:
        total = col.count_documents({})
        pipeline_level = [{"$group": {"_id": "$level", "count": {"$sum": 1}}}]
        level_counts = list(col.aggregate(pipeline_level))
        pipeline_service = [{"$group": {"_id": "$service", "count": {"$sum": 1}}}]
        service_counts = list(col.aggregate(pipeline_service))
        # transform to friendly dicts
        levels = {d['_id'] if d['_id'] is not None else 'unknown': d['count'] for d in level_counts}
        services = {d['_id'] if d['_id'] is not None else 'unknown': d['count'] for d in service_counts}
        return jsonify({'total': total, 'by_level': levels, 'by_service': services}), 200
    except Exception as e:
        return jsonify({'detail': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
