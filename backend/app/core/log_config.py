import logging
import sys


class DevLoggerFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

        self.formatters = {
            logging.DEBUG: logging.Formatter(
                '[%(levelname)s] | %(asctime)s | %(name)s | %(funcName)s:%(lineno)d → %(message)s',
                datefmt='%H:%M:%S'
            ),
            logging.INFO: logging.Formatter(
                '[%(levelname)s] |%(asctime)s | %(name)s | %(funcName)s:%(lineno)d → %(message)s',
                datefmt='%H:%M:%S'
            ),
            logging.WARNING: logging.Formatter(
                '⚠ [%(levelname)s] | %(asctime)s | %(name)s | %(message)s'
            ),
            logging.ERROR: logging.Formatter(
                '✗ [%(levelname)s] | %(asctime)s | %(pathname)s:%(lineno)d → %(message)s'
            ),
            logging.CRITICAL: logging.Formatter(
                '⛔ [%(levelname)s] | %(asctime)s | %(pathname)s:%(lineno)d → %(message)s'
            ),
        }

        self.default_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.default_formatter)
        return formatter.format(record)


def configure_logging(level: str = "INFO", environment: str = 'development'):
    for_dev = False
    if environment.lower() in ("development", "staging"):
        for_dev = True
    root = logging.getLogger()
    root.setLevel(level.upper())

    # Clear any existing handlers (important in FastAPI/Uvicorn)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if for_dev:
        formatter = DevLoggerFormatter()
    else:
        # In prod → plain text or JSON
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Optional: reduce noise from uvicorn/fastapi
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
