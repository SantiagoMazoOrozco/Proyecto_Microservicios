import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL','redis://localhost:6379/0')

# Try to import Celery; if not available we'll provide a synchronous generate_report function only
try:
    from celery import Celery
    celery = Celery('reports', broker=CELERY_BROKER_URL)
except Exception:
    celery = None

from storage import local_path_for_report, report_meta_path, write_meta


def _write_ready_meta(report_id, out):
    meta = {
        'id': report_id,
        'status': 'ready',
        'path': out,
        'generated_at': datetime.utcnow().isoformat()
    }
    write_meta(report_id, meta)


def generate_report(report_id, payload):
    """Synchronous report generation. Tries WeasyPrint, falls back to ReportLab, and handles xlsx."""
    report_type = payload.get('type','pdf')
    title = payload.get('title','Reporte')
    out = local_path_for_report(report_id)

    # If type is xlsx, generate simple excel
    if report_type in ('xlsx', 'excel'):
        try:
            import pandas as pd
            # Expect rows as list of dicts or list of lists
            rows = payload.get('rows') or []
            if isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame(rows)
            out_xlsx = out.replace('.pdf', '.xlsx')
            df.to_excel(out_xlsx, index=False)
            _write_ready_meta(report_id, out_xlsx)
            return {'ok': True, 'path': out_xlsx}
        except Exception as e:
            write_meta(report_id, {'id': report_id, 'status': 'error', 'error': str(e)})
            raise

    # Prefer WeasyPrint for HTML -> PDF
    try:
        from weasyprint import HTML
        html = f"<html><body><h1>{title}</h1><pre>{json.dumps(payload, ensure_ascii=False)}</pre></body></html>"
        HTML(string=html).write_pdf(out)
        _write_ready_meta(report_id, out)
        return {'ok': True, 'path': out}
    except Exception:
        # fallback to reportlab (pure-python)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(out, pagesize=letter)
            text = c.beginText(40, 750)
            text.textLine(title)
            text.textLine('')
            for k, v in payload.items():
                text.textLine(f"{k}: {v}")
            c.drawText(text)
            c.showPage()
            c.save()
            _write_ready_meta(report_id, out)
            return {'ok': True, 'path': out}
        except Exception as e:
            write_meta(report_id, {'id': report_id, 'status': 'error', 'error': str(e)})
            raise


if celery is not None:
    @celery.task
    def generate_report_async(report_id, payload):
        return generate_report(report_id, payload)
