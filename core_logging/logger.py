import os
import sys
import json
import logging # This will now resolve to the standard library python logging!
from datetime import datetime
from typing import Any, Dict
from config.settings import settings

class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func_name": record.funcName,
            "line_number": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)  # type: ignore
            
        return json.dumps(log_data)

def setup_logger(name: str = "midnight_core") -> logging.Logger:
    """Setup and configure a structured logger."""
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(settings.log_level)
    
    # Console handler (standard formatting)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    console_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # JSON File handler (Structured auditing)
    log_dir = os.path.join(settings.storage.base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "audit.jsonl")
    
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(settings.log_level)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()
