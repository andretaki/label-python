"""Configuration for the print agent."""

import os
from pathlib import Path

# Printer configuration
PRINTER_NAME = os.getenv("PRINTER_NAME", "Epson ColorWorks C7500")

# SumatraPDF path (Windows)
SUMATRA_PATH = Path(os.getenv(
    "SUMATRA_PATH",
    r"C:\Program Files\SumatraPDF\SumatraPDF.exe"
))

# Server configuration
HOST = os.getenv("PRINT_AGENT_HOST", "0.0.0.0")
PORT = int(os.getenv("PRINT_AGENT_PORT", "8080"))

# Label style
DEFAULT_LABEL_STYLE = os.getenv("DEFAULT_LABEL_STYLE", "organic")

# Temp directory for generated PDFs
TEMP_DIR = Path(os.getenv("PRINT_AGENT_TEMP_DIR", "/tmp/print_agent"))
