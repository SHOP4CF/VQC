"""
Easy function to easily create new loggers that we can use everywhere in our app
"""
import logging

formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")


def setup_logger(name, log_file, level=logging.WARNING):
    """To setup as many loggers as you want
    Args:
        name (str): name of the logger, using this name we are able to get this logger using GetLogger method
        log_file (str): path where logs will be saved
        level (logging.LEVEL): from which level start to log anything to the files
    It doesn't return logger as if we just create it using getLogger then it is available from that moment
    """
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(handler)

def create_loggers(names, log_files):
    """Takes two arrays with names and locations of log files respectively and creates them

    Args:
        names (list): [list containing names of loggers, after creating them we can use logging.getLogger(name) to obtain it]
        log_files (list): [Locations where to save log of given name]
    """
    for name, log_file in zip(names, log_files):
        setup_logger(name, log_file)