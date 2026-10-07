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