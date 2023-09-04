import logging
import logging.handlers
import json

from core.configurations import Log, Service
from core.utils.general import colored_print

from core.connectors.logger.Axiom import AxiomHandler


class Logger:

    def __init__(self):

        if Log.location not in ["internal", "axiom"]:
            raise Exception("Unknown logging location.")

        log_formatter = logging.Formatter(
            '{"unix_timestamp": "%(asctime)s", "log_type": "%(levelname)s", "message": "%(message)s", "extra": "%(extra)s"}',  # noqa
            datefmt='%s'
        )

        if Log.location == "internal":
            log_file_handler = logging.handlers.RotatingFileHandler(
                'storage/logs.txt',
                maxBytes=10 * 1024 * 1024,  # type: ignore
                backupCount=1
            )
            log_file_handler.setFormatter(log_formatter)
            logging.getLogger("infr").addHandler(log_file_handler)
            colored_print("INFO: Logging is set to internal. Logs will be stored in storage/logs.txt", "green")

        if Log.location == "axiom":
            axiom_handler = AxiomHandler()  # Make sure to initialize this correctly
            axiom_handler.setFormatter(log_formatter)
            logging.getLogger("infr").addHandler(axiom_handler)
            colored_print("INFO: Logging is set to axiom. Logs will be stored in axiom.", "green")

        logging.getLogger("infr").setLevel(logging.INFO)

    def log(self, message, level='INFO', extra={}):
        log = logging.getLogger("infr")
        extra['env_type'] = Service.env_type
        extra['server_host'] = Service.server_host
        extra = {'extra': json.dumps(extra)}
        if level == 'INFO':
            log.info(message, extra=extra)
        elif level == 'WARNING':
            log.warning(message, extra=extra)
        elif level == 'ERROR':
            log.error(message, extra=extra)
        else:
            log.debug(message, extra=extra)


logger = Logger()
