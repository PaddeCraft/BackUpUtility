import logging


def configure(cfg):
    logging.basicConfig(filename=cfg["log_path"], level=logging.DEBUG)


def log(message, error=False):
    if error:
        logging.error(message)
    else:
        logging.info(message)
