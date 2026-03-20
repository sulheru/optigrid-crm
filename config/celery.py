# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/config/celery.py
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("optigrid")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "analyze-open-opportunities-periodic": {
        "task": "apps.opportunities.tasks.analyze_open_opportunities_task",
        "schedule": crontab(minute=f"*/{max(1, int(getattr(settings, 'OPPORTUNITY_ANALYSIS_SCHEDULE_MINUTES', 60)))}"),
        "kwargs": {"force": False},
    },
}
