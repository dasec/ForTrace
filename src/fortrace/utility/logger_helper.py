import logging
import os
import sys
import time

from fortrace_definitions import FORTRACE_ROOT_DIR

log_file_path = os.path.join(FORTRACE_ROOT_DIR, 'log', time.strftime("%Y%m%d_%H%M%S.log"))
formatter = logging.Formatter('[%(threadName)16s] :: %(asctime)s - %(levelname)-8s - %(message)s',
                              defaults={"threadName": "MainThread"})

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a logger with the specified name and log level. The logger will log to console with INFO level, and to the
    log file with the specified one.

    Please refer to https://docs.python.org/3/howto/logging-cookbook.html for more information.
    Especially relevant is https://docs.python.org/3/howto/logging-cookbook.html#patterns-to-avoid

    Args:
        name: name of the logger to be created. Should be __name__ in most cases
        level: the logging level to set the logger to

    Returns:
        a new logger instance
    """
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
