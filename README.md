# Bulk Certificate Generator API

A FastAPI-based backend application for generating certificates in bulk.

The application accepts a list of recipients, validates their details, creates a certificate generation job, processes certificates in the background, tracks job progress, handles individual failures without stopping the complete job, and provides APIs to retrieve generated certificates.

---

## Features

- Bulk certificate generation
- Recipient validation
- Background job processing
- Job status and progress tracking
- Individual recipient failure handling
- Certificate PDF generation
- Certificate retrieval
- SQLite relational database
- REST API using FastAPI
- Automated test suite
- Interactive Swagger API documentation

---

# 1. Project Setup

## Clone the Repository

```bash
git clone https://github.com/Amruthadandigimath/bulk-certificate-generator.git
cd bulk-certificate-generator
```

## Create a Virtual Environment

For Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

After activation, the terminal should show:

```text
(venv)
```

## Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

The main dependencies include:

- FastAPI
- Uvicorn
- SQLAlchemy
- ReportLab
- Pytest
- HTTPX
- Email-validator

---

# 2. How to Run the Application

Make sure the virtual environment is activated.

Run the FastAPI application using:

```bash
uvicorn app.main:app --reload
```

The application will start at:

```text
http://127.0.0.1:8000
```

You can verify the application by opening:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
  "message": "Bulk Certificate Generator API is running"
}
```

---

# 3. API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI allows you to:

- Create certificate generation jobs
- Check job status
- Check job progress
- Retrieve generated certificates
- Test API endpoints directly

---

# 4. How to Run Tests

The project contains automated tests covering the major required functionalities.

Make sure the virtual environment is activated.

Run:

```bash
pytest -v
```

The test suite covers:

- Job creation
- Recipient email validation
- Empty recipient validation
- Certificate generation
- Job status and progress
- Individual certificate generation failure
- Certificate retrieval

Expected result:

```text
7 passed
```

---

# 5. How to Submit a Certificate Generation Request

Use the following endpoint:

```http
POST /api/jobs
```

The request accepts an event name, event date, and a list of recipients.

Example request:

```json
{
  "event_name": "Python Workshop",
  "date": "2026-10-07",
  "recipients": [
    {
      "name": "Alice Johnson",
      "email": "alice@example.com"
    },
    {
      "name": "Bob Smith",
      "email": "bob@example.com"
    },
    {
      "name": "Charlie Brown",
      "email": "charlie@example.com"
    }
  ]
}
```

Example response:

```json
{
  "job_id": "your-job-id",
  "status": "PROCESSING",
  "total": 3
}
```

The returned `job_id` is used to track the certificate generation job.

---

# 6. Recipient Validation

Recipient information is validated using Pydantic.

Each recipient must contain:

```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com"
}
```

The following validations are performed:

- Name cannot be empty
- Email must be a valid email address
- At least one recipient must be provided

For example, an invalid email:

```json
{
  "name": "Alice",
  "email": "invalid-email"
}
```

will result in a validation error.

The API returns HTTP status:

```text
422 Unprocessable Entity
```

---

# 7. How to Check Job Status and Progress

Use:

```http
GET /api/jobs/{job_id}
```

Replace `{job_id}` with the ID returned when creating the job.

Example:

```text
GET /api/jobs/your-job-id
```

Example response:

```json
{
  "job_id": "your-job-id",
  "event_name": "Python Workshop",
  "date": "2026-10-07",
  "status": "COMPLETED",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "progress": 100,
  "recipients": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "status": "SUCCESS",
      "certificate_id": "certificate-id-1",
      "error": null
    }
  ]
}
```

The `progress` value represents the percentage of recipients that have finished processing.

The calculation is:

```text
progress = ((successful + failed) / total) * 100
```

---

# 8. Job Statuses

A job can have the following statuses:

### PROCESSING

The certificate generation job is currently being processed.

### COMPLETED

All certificates were generated successfully.

### COMPLETED_WITH_ERRORS

Some certificates were generated successfully while one or more recipients failed.

### FAILED

The complete job failed to process.

---

# 9. Recipient Statuses

Each recipient is processed independently.

A recipient can have the following status:

```text
PENDING
SUCCESS
FAILED
```

### PENDING

The recipient is waiting to be processed.

### SUCCESS

The certificate was generated successfully.

### FAILED

Certificate generation failed for that particular recipient.

The failure reason is stored in the database.

---

# 10. Individual Failure Handling

One important requirement of the system is that a failure for one recipient must not stop certificate generation for other recipients.

For example, consider three recipients:

```text
Alice   → SUCCESS
Bob     → FAILED
Charlie → SUCCESS
```

The system continues processing Alice and Charlie even though Bob's certificate generation failed.

The failed recipient contains an error message:

```json
{
  "status": "FAILED",
  "error": "Certificate generation error"
}
```

The final job status becomes:

```text
COMPLETED_WITH_ERRORS
```

This ensures that one bad record does not cause the complete batch to fail.

---

# 11. Certificate Generation

Certificates are generated as PDF files using the ReportLab library.

A single predefined certificate template is used for all recipients.

The certificate contains:

- Certificate title
- Recipient name
- Event name
- Event date
- Authorized signature section
- Unique certificate ID

Example generated file:

```text
generated/certificate_<certificate-id>.pdf
```

Each certificate receives a unique UUID.

---

# 12. Certificate Generation Workflow

The overall workflow is:

```text
Client
   |
   v
POST /api/jobs
   |
   v
Validate Request
   |
   v
Create Job
   |
   v
Store Recipients in Database
   |
   v
Background Processing
   |
   v
Process Each Recipient
   |
   +-------------------+
   |                   |
   v                   v
Generate PDF        Generation Error
   |                   |
   v                   v
SUCCESS              FAILED
   |                   |
   +---------+---------+
             |
             v
      Update Job Progress
             |
             v
       Complete Job
```

The generated certificate can then be retrieved using its certificate ID.

---

# 13. How to Retrieve Generated Certificates

Use:

```http
GET /api/jobs/certificates/{certificate_id}
```

Example:

```text
GET /api/jobs/certificates/your-certificate-id
```

The API returns the generated PDF file.

The response has:

```text
Content-Type: application/pdf
```

The certificate can be downloaded directly from the Swagger UI or API client.

---

# 14. Database Design

The application uses SQLite as the relational database.

The database file is:

```text
certificates.db
```

The application contains three main tables.

## Jobs Table

Stores information about each certificate generation job.

Important fields:

```text
id
event_name
event_date
status
total
successful
failed
created_at
```

## Recipients Table

Stores recipient information for each job.

Important fields:

```text
id
job_id
name
email
status
error_message
certificate_id
```

## Certificates Table

Stores information about generated certificates.

Important fields:

```text
id
recipient_id
file_path
created_at
```

The relationships are:

```text
Job
 |
 +---- Recipient
          |
          +---- Certificate
```

---

# 15. Background Processing

FastAPI `BackgroundTasks` is used to process certificate generation after the job creation request is completed.

When a client submits a job:

```text
POST /api/jobs
```

the API:

1. Validates the request.
2. Creates a job record.
3. Stores all recipients.
4. Returns the job ID.
5. Starts certificate processing in the background.

This prevents the API request from having to wait for every certificate to be generated.

---

# 16. Important Implementation / Design Decisions

## FastAPI

FastAPI was selected because it provides:

- Simple REST API development
- Automatic request validation
- Automatic Swagger documentation
- Good support for background tasks
- Type-safe request schemas

## SQLite

SQLite was selected as the relational database because:

- It requires no external database server.
- It is simple to configure.
- It is suitable for this take-home assignment.
- SQLAlchemy provides a clean ORM layer.

## SQLAlchemy

SQLAlchemy is used for:

- Database models
- Relationships
- Database queries
- Transaction management

## ReportLab

ReportLab is used to generate certificate PDFs programmatically.

## BackgroundTasks

FastAPI BackgroundTasks is used to process certificate generation asynchronously from the API request flow.

For a larger production system, a dedicated task queue such as Celery or another distributed job-processing system could be considered.

---

# 17. Error Handling

The application handles errors at both the API and recipient-processing levels.

## API-Level Errors

For example, requesting a non-existing job:

```http
GET /api/jobs/invalid-job-id
```

returns:

```text
404 Not Found
```

with:

```json
{
  "detail": "Job not found"
}
```

## Certificate Errors

If a certificate cannot be generated for one recipient, that recipient is marked:

```text
FAILED
```

and the error message is stored.

Other recipients continue processing.

---

# 18. Certificate Storage

Generated certificates are stored in:

```text
generated/
```

Example:

```text
generated/
├── certificate_123.pdf
├── certificate_456.pdf
└── certificate_789.pdf
```

Generated PDF files are excluded from Git using `.gitignore`.

The database stores the file path associated with each certificate.

---

# 19. Health Check

The API provides a health check endpoint:

```http
GET /api/jobs/health
```

Example response:

```json
{
  "status": "healthy",
  "message": "Jobs API is working"
}
```

This can be used to verify that the Jobs API is running correctly.

---

# 20. Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── jobs.py
│   │
│   └── services/
│       ├── __init__.py
│       └── certificate_generator.py
│
├── generated/
│
├── templates/
│
├── tests/
│   ├── __init__.py
│   └── test_jobs.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

The following files are generated locally and are excluded from Git:

```text
venv/
certificates.db
generated/*.pdf
__pycache__/
.pytest_cache/
```

---

# 21. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs` | Create certificate generation job |
| GET | `/api/jobs/{job_id}` | Check job status and progress |
| GET | `/api/jobs/certificates/{certificate_id}` | Retrieve generated certificate |
| GET | `/api/jobs/health` | Check API health |

---

# 22. Complete Example Workflow

## Step 1: Start the Application

```bash
uvicorn app.main:app --reload
```

## Step 2: Open Swagger

```text
http://127.0.0.1:8000/docs
```

## Step 3: Create a Job

Use:

```http
POST /api/jobs
```

with:

```json
{
  "event_name": "Python Workshop",
  "date": "2026-10-07",
  "recipients": [
    {
      "name": "Alice Johnson",
      "email": "alice@example.com"
    },
    {
      "name": "Bob Smith",
      "email": "bob@example.com"
    }
  ]
}
```

## Step 4: Copy the Job ID

Example:

```text
your-job-id
```

## Step 5: Check Job Status

Use:

```http
GET /api/jobs/your-job-id
```

Wait until the status becomes:

```text
COMPLETED
```

or:

```text
COMPLETED_WITH_ERRORS
```

## Step 6: Copy the Certificate ID

From the recipient information:

```json
{
  "certificate_id": "your-certificate-id"
}
```

## Step 7: Retrieve the Certificate

Use:

```http
GET /api/jobs/certificates/your-certificate-id
```

The generated PDF will be returned.

---

# 23. Testing Summary

The project includes automated tests for the required functionality.

The test suite verifies:

```text
Job Creation
     ↓
Recipient Validation
     ↓
Certificate Generation
     ↓
Job Status
     ↓
Progress Tracking
     ↓
Individual Failure Handling
     ↓
Certificate Retrieval
```

Run all tests using:

```bash
pytest -v
```

Expected result:

```text
7 passed
```

---

# 24. Repository

GitHub Repository:

https://github.com/Amruthadandigimath/bulk-certificate-generator