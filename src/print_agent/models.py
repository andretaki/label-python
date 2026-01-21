"""Pydantic models for print agent request/response."""

from pydantic import BaseModel, Field


class PrintRequest(BaseModel):
    """Request to print a label."""

    sku: str = Field(..., description="Product SKU code")
    lot_number: str = Field(..., description="Lot number in MMYYAL format")
    quantity: int = Field(default=1, ge=1, le=100, description="Number of copies to print")


class PrintResponse(BaseModel):
    """Response from print request."""

    success: bool
    message: str
    job_id: str | None = None
    sku: str | None = None
    lot_number: str | None = None
    quantity: int | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    printer: str
    agent_version: str = "1.0.0"
