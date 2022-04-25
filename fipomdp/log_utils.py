import logging


def get_logger_for_seed(random_seed):
    return logging.getLogger(f"{random_seed}")
