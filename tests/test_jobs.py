from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services import certificate_generator
from app.routes import jobs as jobs_module


client = TestClient(app)


def create_test_job():
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Test Workshop",
            "date": "2026-10-07",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                {
                    "name": "Another User",
                    "email": "another@example.com"
                }
            ]
        }
    )

    return response


# ============================================================
# 1. JOB CREATION
# ============================================================

def test_job_creation():
    response = create_test_job()

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "PROCESSING"
    assert data["total"] == 2


# ============================================================
# 2. INPUT VALIDATION
# ============================================================

def test_invalid_email_validation():
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Test Workshop",
            "date": "2026-10-07",
            "recipients": [
                {
                    "name": "Invalid User",
                    "email": "not-an-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_empty_recipients_validation():
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Test Workshop",
            "date": "2026-10-07",
            "recipients": []
        }
    )

    assert response.status_code == 422


# ============================================================
# 3. CERTIFICATE GENERATION
# ============================================================

def test_certificate_generation(tmp_path, monkeypatch):
    monkeypatch.setattr(
        certificate_generator,
        "OUTPUT_DIR",
        tmp_path
    )

    certificate_id = "test-certificate-123"

    file_path = certificate_generator.generate_certificate(
        name="Test User",
        event_name="Python Workshop",
        event_date="2026-10-07",
        certificate_id=certificate_id
    )

    assert Path(file_path).exists()
    assert Path(file_path).suffix == ".pdf"


# ============================================================
# 4. JOB STATUS AND PROGRESS
# ============================================================

def test_job_status_and_progress():
    response = create_test_job()

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 2
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert data["progress"] == 100
    assert data["status"] == "COMPLETED"


# ============================================================
# 5. INDIVIDUAL FAILURE DOES NOT STOP OTHER RECIPIENTS
# ============================================================

def test_individual_failure_does_not_stop_job(monkeypatch):

    original_generator = jobs_module.generate_certificate

    def failing_generator(
        name,
        event_name,
        event_date,
        certificate_id
    ):

        if name == "Fail User":
            raise Exception("Simulated certificate generation failure")

        return original_generator(
            name=name,
            event_name=event_name,
            event_date=event_date,
            certificate_id=certificate_id
        )

    monkeypatch.setattr(
        jobs_module,
        "generate_certificate",
        failing_generator
    )

    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Failure Test",
            "date": "2026-10-07",
            "recipients": [
                {
                    "name": "Success User",
                    "email": "success@example.com"
                },
                {
                    "name": "Fail User",
                    "email": "fail@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["total"] == 2
    assert data["successful"] == 1
    assert data["failed"] == 1
    assert data["progress"] == 100
    assert data["status"] == "COMPLETED_WITH_ERRORS"

    recipient_statuses = [
        recipient["status"]
        for recipient in data["recipients"]
    ]

    assert "SUCCESS" in recipient_statuses
    assert "FAILED" in recipient_statuses


# ============================================================
# 6. CERTIFICATE RETRIEVAL
# ============================================================

def test_certificate_retrieval():

    response = create_test_job()

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    certificate_id = data["recipients"][0]["certificate_id"]

    certificate_response = client.get(
        f"/api/jobs/certificates/{certificate_id}"
    )

    assert certificate_response.status_code == 200
    assert certificate_response.headers["content-type"] == "application/pdf"
    assert len(certificate_response.content) > 0