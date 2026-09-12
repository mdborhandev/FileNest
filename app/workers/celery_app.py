from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "filenest",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    accept_content=["json"],
    result_serializer="json",
    task_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
