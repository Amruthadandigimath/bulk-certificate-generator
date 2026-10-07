# Bulk Certificate Generator API

A FastAPI-based backend service for generating certificates in bulk. The system accepts a list of recipients, validates their details, generates individual PDF certificates, tracks job progress, handles individual failures independently, and provides APIs to retrieve generated certificates.

## Features

- Bulk certificate generation
- Recipient validation using Pydantic
- Background processing using FastAPI BackgroundTasks
- Job status and progress tracking
- Individual recipient failure handling
- PDF certificate generation using ReportLab
- Certificate retrieval through API
- SQLite relational database using SQLAlchemy
- Automated test suite using Pytest

## Technology Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- ReportLab
- Pydantic
- Pytest
- HTTPX
- Uvicorn

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
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