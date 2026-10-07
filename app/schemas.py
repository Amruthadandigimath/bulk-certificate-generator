from pydantic import BaseModel, EmailStr, Field


class RecipientRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class GenerationRequest(BaseModel):
    event_name: str = Field(..., min_length=1)
    date: str
    recipients: list[RecipientRequest] = Field(
        ...,
        min_length=1
    )


class GenerationResponse(BaseModel):
    job_id: str
    status: str
    total: int