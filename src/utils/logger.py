import logging
from inspect import getframeinfo, stack


class LoggerHelper:
    @staticmethod
    def init_logging(log_path: str):
        try:
            # logging.basicConfig(filename=log_path,
            #                     format='[%(asctime)s] [%(filename)s] [Line:%(lineno)d]  %(levelname)-5s:  %(message)s',
            #                     level=logging.DEBUG)
            logging.basicConfig(filename=log_path,
                                format='[%(asctime)s] [%(levelname)-7s| %(message)s',
                                level=logging.DEBUG)
        # logging is nice to have but we don't want an error with the log to interfere with the code flow
        except Exception as e:
            print(e)

    @staticmethod
    def write_info(msg: str, code_line: int = None):
        try:
            if code_line is None:
                caller = getframeinfo(stack()[1][0])
                code_line = caller.lineno
            logging.info(f" Line {code_line}]:  {msg}")
        # logging is nice to have but we don't want an error with the log to interfere with the code flow
        except Exception as e:
            print(e)

    @staticmethod
    def write_warning(msg: str, code_line: int = None):
        try:
            if code_line is None:
                caller = getframeinfo(stack()[1][0])
                code_line = caller.lineno
            logging.warning(f" Line {code_line}]:  {msg}")
        # logging is nice to have but we don't want an error with the log to interfere with the code flow
        except Exception as e:
            print(e)

    @staticmethod
    def write_error(msg: str, code_line: int = None):
        try:
            if code_line is None:
                caller = getframeinfo(stack()[1][0])
                code_line = caller.lineno
            logging.error(f" Line {code_line}]:  {msg}")
        # logging is nice to have but we don't want an error with the log to interfere with the code flow
        except Exception as e:
            print(e)