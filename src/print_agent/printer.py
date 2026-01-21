"""Printer interface using SumatraPDF for silent printing."""

import platform
import subprocess
from pathlib import Path

from src.print_agent.config import SUMATRA_PATH, PRINTER_NAME


class PrinterError(Exception):
    """Error during printing."""

    pass


def print_pdf(pdf_path: Path, copies: int = 1, printer_name: str | None = None) -> None:
    """
    Print a PDF silently using SumatraPDF (Windows) or lp (Linux/Mac).

    Args:
        pdf_path: Path to the PDF file to print
        copies: Number of copies to print (1-100)
        printer_name: Override default printer name

    Raises:
        PrinterError: If printing fails
        FileNotFoundError: If PDF or SumatraPDF not found
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    printer = printer_name or PRINTER_NAME
    system = platform.system()

    if system == "Windows":
        _print_windows(pdf_path, copies, printer)
    elif system in ("Linux", "Darwin"):
        _print_unix(pdf_path, copies, printer)
    else:
        raise PrinterError(f"Unsupported platform: {system}")


def _print_windows(pdf_path: Path, copies: int, printer: str) -> None:
    """Print using SumatraPDF on Windows."""
    if not SUMATRA_PATH.exists():
        raise FileNotFoundError(
            f"SumatraPDF not found at: {SUMATRA_PATH}\n"
            "Install from https://www.sumatrapdfreader.org/ or set SUMATRA_PATH env var"
        )

    # SumatraPDF command line options:
    # -print-to "printer" : print to specified printer
    # -print-settings "noscale,Nx" : no scaling, N copies
    # -silent : no UI
    cmd = [
        str(SUMATRA_PATH),
        "-print-to", printer,
        "-print-settings", f"noscale,{copies}x",
        "-silent",
        str(pdf_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise PrinterError("Print command timed out after 30 seconds")
    except subprocess.CalledProcessError as e:
        raise PrinterError(f"SumatraPDF failed: {e.stderr or e.stdout or 'Unknown error'}")


def _print_unix(pdf_path: Path, copies: int, printer: str) -> None:
    """Print using lp command on Linux/Mac."""
    # lp command for CUPS printing
    cmd = [
        "lp",
        "-d", printer,
        "-n", str(copies),
        "-o", "fit-to-page",
        str(pdf_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        raise PrinterError("lp command not found. Is CUPS installed?")
    except subprocess.TimeoutExpired:
        raise PrinterError("Print command timed out after 30 seconds")
    except subprocess.CalledProcessError as e:
        raise PrinterError(f"lp failed: {e.stderr or e.stdout or 'Unknown error'}")


def get_printer_status(printer_name: str | None = None) -> dict:
    """
    Get printer status (basic implementation).

    Returns dict with 'available' bool and 'message' string.
    """
    printer = printer_name or PRINTER_NAME
    system = platform.system()

    if system == "Windows":
        # On Windows, just check if SumatraPDF exists
        if SUMATRA_PATH.exists():
            return {"available": True, "message": f"Ready to print to {printer}"}
        else:
            return {"available": False, "message": "SumatraPDF not installed"}

    elif system in ("Linux", "Darwin"):
        # Check if printer exists via lpstat
        try:
            result = subprocess.run(
                ["lpstat", "-p", printer],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return {"available": True, "message": f"Printer {printer} is available"}
            else:
                return {"available": False, "message": f"Printer {printer} not found"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"available": False, "message": "CUPS not available"}

    return {"available": False, "message": f"Unsupported platform: {system}"}
