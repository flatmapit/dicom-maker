"""
DICOM Maker - A native Python CLI application for creating synthetic DICOM data.

This package provides tools for:
- Generating synthetic DICOM studies, series, and images
- Sending DICOM data to PACS systems via C-STORE
- Managing local DICOM studies
- Configuring study templates and PACS connections
"""

__version__ = "0.1.0"
__author__ = "Christopher Gentle"
__email__ = ""

# Import main components for easy access
from .cli import main
from .dicom_generator import DICOMGenerator
from .pacs_client import PACSClient
from .study_manager import StudyManager

__all__ = [
    "main",
    "DICOMGenerator", 
    "PACSClient",
    "StudyManager",
]
