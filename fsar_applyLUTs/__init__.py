import logging, sys

def init_logging(log_file=None, fmt='%(asctime)s %(levelname)s: %(message)s', lvl=logging.INFO):
    try:
        import __main__
        log_id = __main__.__file__
    except AttributeError:
        log_id = '__main__'
    log = logging.getLogger(log_id)
    log.setLevel(lvl)
    log_fmt = logging.Formatter(fmt)

    if log.hasHandlers():
        log.handlers.clear()

    # setup logging to the log file
    if log_file is not None:
        disk_log = logging.FileHandler(log_file)
        disk_log.setFormatter(log_fmt)
        log.addHandler(disk_log)

    # set up logging to stdout
    scrn_log = logging.StreamHandler(sys.stdout)
    scrn_log.setFormatter(log_fmt)
    log.addHandler(scrn_log)

    return log
