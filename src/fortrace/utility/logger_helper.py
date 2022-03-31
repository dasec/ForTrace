from __future__ import absolute_import
import logging
def create_logger(loggerId, loggingLevel):
    """
    Return a logger for the specified loggerId, creating it if necessary.

    If no name is specified, return the root logger.

    """
    # create logger
    logger = logging.getLogger(loggerId)
    logger.setLevel(loggingLevel)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(loggingLevel)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger
