import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..models import Certificate, Job, Recipient
from ..schemas import GenerationRequest, GenerationResponse
from ..services.certificate_generator import generate_certificate


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# ============================================================
# 1. BACKGROUND CERTIFICATE GENERATION
# ============================================================

def process_job(job_id: str):
    """
    Generate certificates for all recipients in a job.

    Each recipient is processed independently.
    If one certificate fails, the remaining certificates
    will continue to generate.
    """

    db = SessionLocal()

    try:
        # Find the job
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            return

        # Get all recipients for this job
        recipients = (
            db.query(Recipient)
            .filter(Recipient.job_id == job_id)
            .all()
        )

        # Process each recipient independently
        for recipient in recipients:

            # Skip already processed recipients
            if recipient.status in ["SUCCESS", "FAILED"]:
                continue

            try:
                # Create unique certificate ID
                certificate_id = str(uuid.uuid4())

                # Generate the PDF certificate
                file_path = generate_certificate(
                    name=recipient.name,
                    event_name=job.event_name,
                    event_date=job.event_date,
                    certificate_id=certificate_id
                )

                # Save certificate information
                certificate = Certificate(
                    id=certificate_id,
                    recipient_id=recipient.id,
                    file_path=file_path
                )

                db.add(certificate)

                # Update recipient
                recipient.status = "SUCCESS"
                recipient.certificate_id = certificate_id
                recipient.error_message = None

                # Increase successful count
                job.successful += 1

            except Exception as error:

                # Mark only this recipient as failed
                recipient.status = "FAILED"
                recipient.error_message = str(error)

                # Increase failed count
                job.failed += 1

            # Save progress after every recipient
            db.commit()

        # ====================================================
        # DETERMINE FINAL JOB STATUS
        # ====================================================

        if job.failed == 0:
            job.status = "COMPLETED"

        elif job.successful == 0:
            job.status = "FAILED"

        else:
            job.status = "COMPLETED_WITH_ERRORS"

        db.commit()

    except Exception as error:

        print(f"Job processing failed: {error}")

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if job:
            job.status = "FAILED"
            db.commit()

    finally:
        db.close()


# ============================================================
# 2. CREATE GENERATION JOB
# ============================================================

@router.post(
    "",
    response_model=GenerationResponse
)
def create_generation_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Create Job record
    job = Job(
        id=job_id,
        event_name=request.event_name,
        event_date=request.date,
        status="PROCESSING",
        total=len(request.recipients),
        successful=0,
        failed=0
    )

    db.add(job)

    # ========================================================
    # CREATE RECIPIENT RECORDS
    # ========================================================

    for recipient_data in request.recipients:

        recipient = Recipient(
            job_id=job_id,
            name=recipient_data.name,
            email=recipient_data.email,
            status="PENDING"
        )

        db.add(recipient)

    # Save job and recipients
    db.commit()

    # ========================================================
    # START BACKGROUND PROCESSING
    # ========================================================

    background_tasks.add_task(
        process_job,
        job_id
    )

    # Return immediately
    return GenerationResponse(
        job_id=job_id,
        status="PROCESSING",
        total=len(request.recipients)
    )


# ============================================================
# 3. HEALTH CHECK
# ============================================================

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "message": "Jobs API is working"
    }


# ============================================================
# 4. GET / DOWNLOAD CERTIFICATE
# ============================================================

@router.get("/certificates/{certificate_id}")
def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):

    # Find certificate
    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    # Certificate doesn't exist
    if not certificate:

        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    # Get file path
    file_path = Path(certificate.file_path)

    # Check whether PDF exists
    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    # Return PDF
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name
    )


# ============================================================
# 5. GET JOB STATUS
# ============================================================

@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):

    # Find job
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )
    

    # Job doesn't exist
    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # ========================================================
    # CALCULATE PROGRESS
    # ========================================================

    completed = job.successful + job.failed

    progress = 0

    if job.total > 0:

        progress = round(
            (completed / job.total) * 100,
            2
        )

    # ========================================================
    # GET RECIPIENT INFORMATION
    # ========================================================

    recipients = (
        db.query(Recipient)
        .filter(Recipient.job_id == job_id)
        .all()
    )

    recipient_data = []

    for recipient in recipients:

        recipient_data.append(
            {
                "id": recipient.id,
                "name": recipient.name,
                "email": recipient.email,
                "status": recipient.status,
                "certificate_id": recipient.certificate_id,
                "error": recipient.error_message
            }
        )

    # ========================================================
    # RETURN JOB STATUS
    # ========================================================

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "date": job.event_date,
        "status": job.status,
        "total": job.total,
        "successful": job.successful,
        "failed": job.failed,
        "progress": progress,
        "recipients": recipient_data
    }