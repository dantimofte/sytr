import logging
import os


def initlog(name, level=logging.INFO):
    root_logger = logging.getLogger(name)
    root_logger.setLevel(level)

    my_ch = logging.StreamHandler()
    my_ch.setLevel(level)
    pid = os.getpid()

    formatter_console = logging.Formatter(
        f'%(asctime)s {pid} %(levelname) -10s %(name) -10s %(lineno) -5d  %(message)s'
    )
    my_ch.setFormatter(formatter_console)
    if not root_logger.handlers:
        root_logger.addHandler(my_ch)
    return root_logger
