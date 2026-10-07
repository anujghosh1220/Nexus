from app.workers.celery_app import celery_app


@celery_app.task(bind=True)
def test_task(self, message: str = "Hello from Celery") -> dict:
    """Test background task."""
    return {"status": "success", "message": message}


@celery_app.task(bind=True)
def cleanup_task(self) -> dict:
    """Cleanup expired data."""
    return {"status": "success", "cleaned": True}


@celery_app.task(bind=True)
def analytics_task(self, event_type: str, data: dict) -> dict:
    """Process analytics event."""
    return {"status": "success", "event_type": event_type}
