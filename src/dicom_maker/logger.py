"""
Logging system for DICOM Maker

Copyright (c) 2025 flatmapit.com
Licensed under the MIT License
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)


class DICOMMakerLogger:
    """Custom logger for DICOM Maker with CLI and file logging."""
    
    def __init__(self, log_file: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize the logger.
        
        Args:
            log_file: Path to log file (optional)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger("dicom_maker")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        self.cli_formatter = self._create_cli_formatter()
        self.file_formatter = self._create_file_formatter()
        
        # Add console handler
        self._add_console_handler()
        
        # Add file handler if specified
        if log_file:
            self._add_file_handler(log_file)
    
    def _create_cli_formatter(self) -> logging.Formatter:
        """Create formatter for CLI output with colors."""
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                # Add color based on log level
                if record.levelno >= logging.ERROR:
                    record.levelname = f"{Fore.RED}{record.levelname}{Style.RESET_ALL}"
                elif record.levelno >= logging.WARNING:
                    record.levelname = f"{Fore.YELLOW}{record.levelname}{Style.RESET_ALL}"
                elif record.levelno >= logging.INFO:
                    record.levelname = f"{Fore.GREEN}{record.levelname}{Style.RESET_ALL}"
                else:
                    record.levelname = f"{Fore.CYAN}{record.levelname}{Style.RESET_ALL}"
                
                return super().format(record)
        
        return ColoredFormatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
    
    def _create_file_formatter(self) -> logging.Formatter:
        """Create formatter for file output."""
        return logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def _add_console_handler(self):
        """Add console handler for CLI output."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.cli_formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self, log_file: str):
        """Add file handler for persistent logging."""
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message with special formatting."""
        self.logger.info(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}", **kwargs)
    
    def failure(self, message: str, **kwargs):
        """Log failure message with special formatting."""
        self.logger.error(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", **kwargs)
    
    def progress(self, message: str, **kwargs):
        """Log progress message with special formatting."""
        self.logger.info(f"{Fore.CYAN}→ {message}{Style.RESET_ALL}", **kwargs)
    
    def generated_data(self, field_name: str, value: str, **kwargs):
        """Log when data is automatically generated."""
        self.logger.warning(
            f"{Fore.YELLOW}Generated {field_name}: {value}{Style.RESET_ALL}", 
            **kwargs
        )


# Global logger instance
_logger: Optional[DICOMMakerLogger] = None


def get_logger() -> DICOMMakerLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = DICOMMakerLogger()
    return _logger


def setup_logging(log_file: Optional[str] = None, log_level: str = "INFO") -> DICOMMakerLogger:
    """
    Set up logging for the application.
    
    Args:
        log_file: Path to log file (optional)
        log_level: Logging level
        
    Returns:
        Configured logger instance
    """
    global _logger
    _logger = DICOMMakerLogger(log_file, log_level)
    return _logger


def log_dicom_field_generation(tag: str, field_name: str, generated_value: str, reason: str = "not specified"):
    """
    Log when a DICOM field is automatically generated.
    
    Args:
        tag: DICOM tag (e.g., "0010,0010")
        field_name: Human-readable field name
        generated_value: The generated value
        reason: Reason for generation
    """
    logger = get_logger()
    logger.generated_data(
        f"DICOM field {field_name} ({tag})", 
        generated_value,
        extra={"tag": tag, "reason": reason}
    )
