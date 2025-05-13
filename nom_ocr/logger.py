import logging

map_level = {
    "DEBUG" : logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL 
}

class Logger(logging.Logger):
    def __init__(self, name, stdout='DEBUG', file='DEBUG', file_name=None):
        super().__init__(name=name, level=logging.NOTSET)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if stdout:
            stdout_handler = logging.StreamHandler()
            stdout_handler.setLevel(map_level[stdout])
            stdout_handler.setFormatter(formatter)
            try:
                stdout_handler.stream.reconfigure(encoding='utf-8')  # Fix Unicode Windows
            except AttributeError:
                pass
            self.addHandler(stdout_handler)
        
        if file and file_name:
            file_handler = logging.FileHandler(file_name,encoding="utf-8")
            file_handler.setLevel(map_level[file])
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

if __name__  == "__main__":
    logger = Logger('VOCR', file_name="error.log")

    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')