from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "crypto_price_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.prices"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.tasks.prices.fetch_and_store_prices",
        "schedule": crontab(minute="*"),
    }
}
