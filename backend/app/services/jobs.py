from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import Job


def run_sync_job(
    db: Session,
    job_type: str,
    payload: dict[str, Any],
    worker: Callable[[Session, dict[str, Any]], dict[str, Any]],
) -> Job:
    job = Job(type=job_type, status="queued", payload_json=payload)
    db.add(job)
    db.commit()
    db.refresh(job)

    job.status = "running"
    job.started_at = datetime.now(UTC)
    db.commit()
    try:
        result = worker(db, payload)
        job.result_json = result
        job.status = "succeeded"
    except Exception as exc:
        db.rollback()
        job = db.get(Job, job.id)
        if job is None:
            raise
        job.error = str(exc)
        job.status = "failed"
    job.finished_at = datetime.now(UTC)
    db.commit()
    db.refresh(job)
    return job
