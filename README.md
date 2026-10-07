# Bulk Certificate Generator API

A FastAPI-based backend service for generating certificates in bulk.

The application accepts a list of recipients, validates their details, creates a certificate generation job, processes certificates in the background, tracks job progress, handles individual recipient failures without stopping the complete job, and provides an API to retrieve generated certificates.

---

## Features

- Bulk certificate generation
- Recipient validation
- Background certificate processing
- Job status tracking
- Real-time progress information
- Individual recipient failure handling
- PDF certificate generation
- Certificate retrieval through API
- Relational database using SQLite and SQLAlchemy
- Automated tests using Pytest
- Interactive API documentation using Swagger UI

---

## Technology Stack

- **Python 3.11**
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM and database management
- **SQLite** - Relational database
- **ReportLab** - PDF certificate generation
- **Pydantic** - Request validation
- **Pytest** - Automated testing
- **Uvicorn** - ASGI server
- **HTTPX** - API testing

---

# 1. Project Setup

## Prerequisites

Make sure the following are installed:

- Python 3.11 or later
- Git
- pip

## Clone the Repository

```bash
git clone https://github.com/Amruthadandigimath/bulk-certificate-generator.git
cd bulk-certificate-generator
Create a Virtual Environment
For Windows:
python -m venv venv

Activate the Virtual Environment
For Windows PowerShell:
venv\Scripts\activate

After activation, the terminal should show:
(venv)

Install Dependencies
pip install -r requirements.txt

The project uses SQLite, so no separate database server is required.
2. How to Run the Application
Start the FastAPI application using:
uvicorn app.main:app --reload

The application will be available at:
http://127.0.0.1:8000

Swagger API Documentation
FastAPI provides interactive API documentation using Swagger UI.
Open:
http://127.0.0.1:8000/docs

Swagger UI can be used to submit certificate generation requests, check job status, and retrieve generated certificates.
3. How to Run Tests
The project uses Pytest for automated testing.
Run:
pytest -v

The test suite covers:
- Job creation
- Invalid email validation
- Empty recipient validation
- Certificate generation
- Job status and progress
- Individual recipient failure handling
- Certificate retrieval
The project contains 7 automated tests and all 7 tests pass successfully.
Example result:
7 passed

4. How to Submit a Certificate Generation Request
A certificate generation request is submitted using:
POST /api/jobs

The request contains:
- Event name
- Event date
- List of recipients
- Recipient name
- Recipient email
Using Swagger
1. Start the application.
2. Open:
http://127.0.0.1:8000/docs

3. Find POST /api/jobs.
4. Click Try it out.
5. Enter the request JSON.
6. Click Execute.
Example Request
{
  "event_name": "Python Workshop",
  "date": "2026-10-07",
  "recipients": [
    {
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "name": "Jane Doe",
      "email": "jane@example.com"
    },
    {
      "name": "Alex Smith",
      "email": "alex@example.com"
    }
  ]
}

Example Response
{
  "job_id": "your-job-id",
  "status": "PROCESSING",
  "total": 3
}

The returned job_id is used to track the progress of the certificate generation job.
5. How to Check Job Status and Progress
Use:
GET /api/jobs/{job_id}

Replace {job_id} with the ID returned when the job was created.
Example:
GET /api/jobs/your-job-id

The response provides:
- Job ID
- Event name
- Event date
- Job status
- Total recipients
- Successful certificates
- Failed certificates
- Progress percentage
- Individual recipient status
- Certificate IDs
- Error messages for failed recipients
Example Response
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
      "name": "John Doe",
      "email": "john@example.com",
      "status": "SUCCESS",
      "certificate_id": "certificate-uuid",
      "error": null
    }
  ]
}

Progress Calculation
Progress is calculated using:
progress = (successful + failed) / total × 100

For example:
Total recipients: 10
Successful: 8
Failed: 1
Completed: 9

Progress: 90%

When all recipients have been processed, progress becomes 100%.
6. How to Retrieve Generated Certificates
After a recipient is successfully processed, the job status response contains a certificate_id.
Use:
GET /api/jobs/certificates/{certificate_id}

Example:
GET /api/jobs/certificates/your-certificate-id

The API returns the generated certificate as a PDF file.
Using Swagger
1. Open:
http://127.0.0.1:8000/docs

2. Find:
GET /api/jobs/certificates/{certificate_id}

3. Click Try it out.
4. Enter the certificate_id obtained from the job status response.
5. Click Execute.
6. The generated PDF can be downloaded from the response.
Generated certificate files are stored in:
generated/

7. Important Implementation / Design Decisions
FastAPI
FastAPI was selected because it provides:
- Simple REST API development
- Automatic request validation
- Interactive Swagger documentation
- Background task support
- Clean API structure
Background Processing
FastAPI BackgroundTasks is used to process certificate generation after the job request is accepted.
This allows the API to return a job_id without making the client wait for all certificates to finish generating.
For this assignment, FastAPI BackgroundTasks is sufficient.
For a production-scale system, a durable task queue such as Celery with a message broker could be introduced.
SQLite and SQLAlchemy
SQLite was selected as a lightweight relational database suitable for this assignment.
SQLAlchemy is used as the ORM to manage database operations and keep the database layer modular.
The application can be migrated to another relational database with minimal changes.
ReportLab
ReportLab is used to generate PDF certificates programmatically.
A predefined certificate layout is used, and recipient-specific information such as:
- Recipient name
- Event name
- Event date
- Certificate ID
is inserted during certificate generation.
Individual Failure Handling
Each recipient is processed independently.
If certificate generation fails for one recipient, the failure is recorded and processing continues for the remaining recipients.
For example:
Recipient 1 → SUCCESS
Recipient 2 → FAILED
Recipient 3 → SUCCESS
Recipient 4 → SUCCESS

The failure of one recipient does not stop the complete bulk generation job.
If some recipients succeed and some fail, the final job status becomes:
COMPLETED_WITH_ERRORS

Database Tracking
The database stores:
- Job information
- Recipient information
- Processing status
- Error messages
- Certificate IDs
- Certificate file paths
This allows the application to track the complete certificate generation process.
8. API Endpoints
Method	Endpoint	Description
POST	/api/jobs	Create a bulk certificate generation job
GET	/api/jobs/{job_id}	Get job status and progress
GET	/api/jobs/certificates/{certificate_id}	Retrieve generated certificate PDF
GET	/api/jobs/health	Check API health


9. Recipient Validation
Incoming recipient information is validated using Pydantic.
Each recipient must contain:
{
  "name": "John Doe",
  "email": "john@example.com"
}

The API validates:
- Name must not be empty
- Email must be valid
- At least one recipient must be provided
Invalid requests return:
422 Unprocessable Entity

10. Job and Recipient Statuses
Possible job statuses are:
PROCESSING
COMPLETED
COMPLETED_WITH_ERRORS
FAILED

Possible recipient statuses are:
PENDING
SUCCESS
FAILED

11. Certificate Generation Workflow
Client
  |
  | POST /api/jobs
  v
FastAPI API
  |
  | Validate Request
  v
Create Job + Recipients
  |
  | Return Job ID
  v
Background Processing
  |
  +--------------------+
  |                    |
  v                    v
Recipient 1          Recipient 2
  |                    |
  v                    v
Generate PDF        Generate PDF
  |                    |
  v                    v
SUCCESS             SUCCESS/FAILED
  |                    |
  +----------+---------+
             |
             v
      Update Job Status
             |
             v
      GET Job Status
             |
             v
     Get Certificate ID
             |
             v
   GET Certificate PDF

12. Database Design
The application uses SQLite with SQLAlchemy.
There are three main database tables.
Jobs
Stores information about each certificate generation job.
Important fields:
- Job ID
- Event name
- Event date
- Status
- Total recipients
- Successful count
- Failed count
- Creation time
Recipients
Stores information about individual recipients.
Important fields:
- Recipient ID
- Job ID
- Name
- Email
- Status
- Error message
- Certificate ID
Certificates
Stores information about generated certificates.
Important fields:
- Certificate ID
- Recipient ID
- File path
- Creation time
Relationship:
Job
 |
 | 1-to-many
 v
Recipients
 |
 | certificate reference
 v
Certificate

13. Project Structure
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
├── tests/
│   ├── __init__.py
│   └── test_jobs.py
│
├── generated/
├── requirements.txt
├── .gitignore
└── README.md

14. Error Handling
The application handles errors at both request and certificate-generation levels.
Request Validation
Invalid recipient data is rejected before processing.
Examples:
- Empty recipient name
- Invalid email address
- Empty recipient list
Certificate Generation Errors
If certificate generation fails for an individual recipient, the error is stored against that recipient.
The remaining recipients continue to be processed.
This ensures that a single failure does not terminate the entire bulk operation.
15. Health Check
The API provides a health check endpoint:
GET /api/jobs/health

Example response:
{
  "status": "healthy",
  "message": "Jobs API is working"
}

16. Generated Certificate Storage
Generated certificates are stored in:
generated/

Each certificate is assigned a unique certificate ID.
The generated file follows the format:
certificate_<certificate_id>.pdf

Generated PDF files and the SQLite database are excluded from Git using .gitignore.
17. Complete Example Workflow
Step 1: Start the application
uvicorn app.main:app --reload

Step 2: Open Swagger
http://127.0.0.1:8000/docs

Step 3: Submit a certificate generation request
Use:
POST /api/jobs

with the event information and recipient list.
Step 4: Copy the returned job ID
your-job-id

Step 5: Check job status
Use:
GET /api/jobs/{job_id}

Step 6: Get the certificate ID
After successful processing, obtain the certificate_id from the recipient information.
Step 7: Retrieve the certificate
Use:
GET /api/jobs/certificates/{certificate_id}

The generated PDF certificate will be returned.