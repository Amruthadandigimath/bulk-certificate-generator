from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    event_name = Column(String, nullable=False)
    event_date = Column(String, nullable=False)

    status = Column(String, default="PENDING")

    total = Column(Integer, default=0)
    successful = Column(Integer, default=0)
    failed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    recipients = relationship(
        "Recipient",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        String,
        ForeignKey("jobs.id"),
        nullable=False
    )

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    status = Column(String, default="PENDING")

    error_message = Column(Text, nullable=True)

    certificate_id = Column(String, nullable=True)

    job = relationship(
        "Job",
        back_populates="recipients"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, index=True)

    recipient_id = Column(
        Integer,
        ForeignKey("recipients.id"),
        nullable=False
    )

    file_path = Column(String, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )