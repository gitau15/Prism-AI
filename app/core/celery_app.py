from celery import Celery
from app.core.config import settings

# Create the Celery app instance
celery_app = Celery(
    "prism_ai_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Automatically discover tasks in the following modules
    include=[
        "app.core.celery_tasks",
    ],
)

# Configure task routes (optional)
celery_app.conf.task_routes = {
    "app.core.celery_tasks.process_document_task": "document-processing",
}