"""FastAPI print agent server.

Receives print requests via HTTP and prints labels using the existing
label renderer and SumatraPDF.

Usage:
    uvicorn src.print_agent.main:app --host 0.0.0.0 --port 8080

Or run directly:
    python -m src.print_agent.main
"""

import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.print_agent.config import PRINTER_NAME, HOST, PORT, DEFAULT_LABEL_STYLE
from src.print_agent.models import PrintRequest, PrintResponse, HealthResponse
from src.print_agent.printer import print_pdf, get_printer_status, PrinterError

app = FastAPI(
    title="Label Print Agent",
    description="Local print agent for Alliance Chemical label printing",
    version="1.0.0",
)

# Allow CORS from Vercel and localhost during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "https://print.alliancechemical.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check agent and printer status."""
    status = get_printer_status()
    return HealthResponse(
        status="ok" if status["available"] else "degraded",
        printer=PRINTER_NAME,
    )


@app.post("/print", response_model=PrintResponse)
def print_label(req: PrintRequest):
    """
    Generate and print a label.

    The label is generated using the existing organic label renderer,
    then printed via SumatraPDF (Windows) or lp (Unix).
    """
    job_id = str(uuid.uuid4())

    try:
        # Import here to avoid circular imports
        from src.label_renderer_organic import generate_organic_label

        # Generate PDF in temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # Generate the label PDF
            pdf_path = generate_organic_label(
                sku=req.sku,
                lot_number=req.lot_number,
                output_dir=output_dir,
            )

            # Print the PDF
            print_pdf(pdf_path, copies=req.quantity)

        return PrintResponse(
            success=True,
            message=f"Printed {req.quantity} label(s) for {req.sku}",
            job_id=job_id,
            sku=req.sku,
            lot_number=req.lot_number,
            quantity=req.quantity,
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"SKU not found: {req.sku}. Error: {str(e)}",
        )

    except PrinterError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Printer error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}",
        )


@app.get("/")
def root():
    """Root endpoint with basic info."""
    return {
        "name": "Label Print Agent",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "print": "POST /print",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
