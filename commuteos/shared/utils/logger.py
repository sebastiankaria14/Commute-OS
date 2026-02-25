"""
Structured logging utility for CommuteOS.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from ..config.settings import get_settings


class StructuredLogger:
    """Structured JSON logger for production environments."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        settings = get_settings()
        
        # Set log level
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Set formatter based on config
        if settings.LOG_FORMAT == "json":
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal log method with structured data."""
        log_method = getattr(self.logger, level)
        log_method(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info level message."""
        self._log("info", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error level message."""
        self._log("error", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message."""
        self._log("warning", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message."""
        self._log("debug", message, **kwargs)


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename', 
                              'funcName', 'levelname', 'levelno', 'lineno',
                              'module', 'msecs', 'message', 'pathname', 
                              'process', 'processName', 'relativeCreated',
                              'thread', 'threadName', 'exc_info', 'exc_text',
                              'stack_info']:
                    log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
