import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.entities import Job

logger = logging.getLogger("websmith.jobs")


def run_sync_job(
    db: Session,
    job_type: str,
    payload: dict[str, Any],
    worker: Callable[[Session, dict[str, Any]], dict[str, Any]],
) -> Job:
    """Run a worker synchronously and persist its lifecycle in one atomic transaction.

    The job row and the worker's writes commit together exactly once on success, so a crash
    mid-run never leaves a half-written success. On failure we roll back the worker's partial
    writes, then record the error on a fresh job row and commit only that.
    """
    job = Job(
        type=job_type,
        status="running",
        payload_json=payload,
        started_at=datetime.now(UTC),
    )
    db.add(job)
    db.flush()  # assign job.id without committing; keeps everything in one transaction
    job_id = job.id

    try:
        result = worker(db, payload)
        job.result_json = result
        job.status = "succeeded"
        job.finished_at = datetime.now(UTC)
        db.commit()
    except Exception as exc:
        logger.exception("Job %s (%s) failed", job_id, job_type)
        db.rollback()  # discard the worker's partial writes
        # Re-record failure on its own committed transaction.
        failed = db.get(Job, job_id) or Job(id=job_id, type=job_type, payload_json=payload)
        failed.status = "failed"
        failed.error = str(exc) or exc.__class__.__name__
        failed.started_at = failed.started_at or datetime.now(UTC)
        failed.finished_at = datetime.now(UTC)
        db.add(failed)
        db.commit()
        db.refresh(failed)
        return failed

    db.refresh(job)
    return job


def recover_stuck_jobs(db: Session) -> int:
    """Mark jobs left in 'running' (e.g. by a crash/restart) as failed. Returns the count."""
    result = db.execute(
        update(Job)
        .where(Job.status == "running")
        .values(
            status="failed",
            error="Interrupted: process restarted while the job was running.",
            finished_at=datetime.now(UTC),
        )
    )
    db.commit()
    count = result.rowcount or 0
    if count:
        logger.warning("Recovered %d stuck job(s) on startup", count)
    return count
