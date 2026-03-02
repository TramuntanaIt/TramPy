import logging
import os
import sys
from datetime import datetime

def _base_dir():
    # EXE (PyInstaller)
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # Executant .py
    return os.path.dirname(os.path.abspath(sys.argv[0]))

def setup_custom_logger(name: str):
    base = _base_dir()
    logs_dir = os.path.join(base, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    log_path = os.path.join(logs_dir, f"etl_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger