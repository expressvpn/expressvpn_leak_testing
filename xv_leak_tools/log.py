import logging
import os
import tempfile
import sys

import colorlog

from xv_leak_tools.helpers import merge_two_dicts

def _mktemp(suffix):
    filehandle, path = tempfile.mkstemp(suffix=suffix, prefix='xv_leak_test_')
    os.close(filehandle)
    return path

# TODO: Consider making describe fancy. Perhaps have it ennumerate test steps and have a title
# TODO: Document how log levels should be used
# TODO: Might need to refactor all of this. I want to send error to stderr and the rest to stdout
# for example

class LeakTestLogger:

    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    VERBOSE = logging.DEBUG - 5

    # static initialization
    logging.addLevelName(VERBOSE, "VERBOSE")

    DEFAULT_CONFIG = {
        'trace': {
            'stream_format': '%(log_color)s %(asctime)s %(levelname)s: %(message)s',
            'file_format': None,
            'logfile': None,
            'level': logging.INFO,
            'log_colors': {'WARNING' : 'bold_yellow', 'ERROR': 'bold_red'},
        },
        'instruction': {
            'stream_format': '%(log_color)s %(asctime)s INTERACTIVE: \n%(message)s',
            'file_format': None,
            'logfile': None,
            'level': logging.INFO,
            'log_colors': {'INFO' : 'bold_green'},
        },
        'describe': {
            'stream_format': '%(log_color)s %(asctime)s DESCRIBE: %(message)s',
            'file_format': '%(message)s',
            'logfile': _mktemp('_describe.txt'),
            'level': logging.INFO,
            'log_colors': {'INFO' : 'cyan'},
        },
        'report': {
            'stream_format': None,
            'file_format': '%(message)s',
            'logfile': _mktemp('_report.txt'),
            'level': logging.INFO,
            'log_colors': None,
        },
    }

    CURRENT_CONFIG = DEFAULT_CONFIG.copy()

    @staticmethod
    # pylint: disable=too-many-arguments
    def _configure_logger(logger_name, stream_format, file_format, logfile, level, log_colors):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        # Clear any existing handlers
        logger.handlers = []

        if file_format and logfile:
            file_handler = logging.FileHandler(logfile, mode='a', encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(file_format))
            logger.addHandler(file_handler)

        if stream_format:
            formatter = colorlog.TTYColoredFormatter(fmt=stream_format, log_colors=log_colors)
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    @staticmethod
    def configure(config=None):
        if config is None:
            config = {}

        for logger_name, settings in list(config.items()):
            LeakTestLogger.CURRENT_CONFIG[logger_name] = merge_two_dicts(
                LeakTestLogger.CURRENT_CONFIG[logger_name], settings)

        # Configure trace first so we can use it to log info about the other loggers.
        trace_settings = LeakTestLogger.CURRENT_CONFIG['trace']
        LeakTestLogger._configure_logger('trace', **trace_settings)

        for logger_name, settings in list(LeakTestLogger.CURRENT_CONFIG.items()):
            if logger_name == 'trace':
                continue
            LeakTestLogger._configure_logger(logger_name, **settings)

    @staticmethod
    def terminate():
        for _, logger in logging.Logger.manager.loggerDict.items():
            if isinstance(logger, logging.PlaceHolder):
                continue
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.close()

    # TODO: These are suboptimal as they getLogger each time. Any real performance hit here?
    # TODO: Consider finding all newlines in the msg and ensuring the log prefix is added for each
    # newline. Would improve formatting for certain stuff.
    @staticmethod
    def error(msg):
        logging.getLogger('trace').error(msg)

    @staticmethod
    def warning(msg):
        logging.getLogger('trace').warning(msg)

    @staticmethod
    def info(msg):
        logging.getLogger('trace').info(msg)

    @staticmethod
    def debug(msg):
        logging.getLogger('trace').debug(msg)

    @staticmethod
    def verbose(msg):
        logging.getLogger('trace').log(LeakTestLogger.VERBOSE, msg)

    @staticmethod
    def report(msg):
        logging.getLogger('report').info(msg)

    @staticmethod
    def instruction(msg):
        logging.getLogger('instruction').info(msg)

    @staticmethod
    def describe(msg):
        logging.getLogger('describe').info(msg)

# TODO: Are we happy with this?!
L = LeakTestLogger # pylint: disable=invalid-name
