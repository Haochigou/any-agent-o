import os
import logging
from logging import handlers

_file_handlers = {}

def getLogger(name, level="DEBUG"):
    '''获取日志句柄'''
    if _file_handlers.get(name):
        return _file_handlers.get(name)
    
    logfile_dir = os.getenv("LOG_DIR")
    if logfile_dir is not None:
        if not os.path.exists(logfile_dir):
            os.mkdir(logfile_dir)
    else:
        logfile_dir = ""
        
    fullpath = os.path.join(logfile_dir, name+".log")
    print(f'---------logging into {fullpath}-------------')
    my_log_collector = logging.getLogger(fullpath)
    log_handler = handlers.RotatingFileHandler(fullpath, maxBytes = 1024 * 1024 * 10, backupCount=100)
    formatter = logging.Formatter('%(asctime)s [%(pathname)s-->line:%(lineno)d] - %(levelname)s: %(message)s')
    log_handler.setFormatter(formatter)
    my_log_collector.addHandler(log_handler)
    my_log_collector.setLevel(level)
    _file_handlers[name] = my_log_collector

    return my_log_collector
