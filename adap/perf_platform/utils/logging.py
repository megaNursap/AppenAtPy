from adap.settings import Config
import logging
import sys
import os

DEBUGV = 9


class CustomLogger(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        logging.addLevelName(DEBUGV, "DEBUGV")

    def debugv(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUGV):
            self._log(DEBUGV, msg, args, **kwargs)


logging.setLoggerClass(CustomLogger)


def create_logger(logger_name: str, stdout=Config.LOG_TO_STDOUT):
    """ create and instance of Logger class """

    logger = logging.getLogger(logger_name)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.setLevel(Config.LOG_LEVEL)
    handler.setLevel(Config.LOG_LEVEL)

    if stdout and not os.environ.get('PYTEST_CURRENT_TEST'):
        logger.addHandler(handler)

    return logger


class LogToDB(logging.Filter):
    """
    Subclass of Filter for sending logs to DB

    Only logs above Config.LOG_TO_DB_LEVEL level will be sent to DB
    """
    def __init__(self):
        from .results_handler import log_to_db
        self.log_to_db = log_to_db

    def filter(self, record):
        if record.levelno >= logging.getLevelName(Config.LOG_TO_DB_LEVEL):
            self.log_to_db(
                level=record.levelname,
                msg=record.msg
                )
        return True


def set_LogToDB(logger):
    f = LogToDB()
    logger.addFilter(f)


def get_logger(logger_name: str, db=None, **kwargs):
    """
    Get an instance of Logger (CustomLogger)

    Parameters:
    db (bool): if set to True, logs will be sent to DB;
               if set to False, logs will not be sent to DB;
               if set to None (default) AND if
                    Config.CAPTURE_RESULTS is set to True (default is False)
                    then logs will be sent to DB
    """

    logger = create_logger(logger_name, **kwargs)
    if db or (db is None and Config.CAPTURE_RESULTS):
        set_LogToDB(logger)
    return logger
