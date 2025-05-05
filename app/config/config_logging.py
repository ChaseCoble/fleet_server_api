import logging
import os
import datetime

def setup_logger(log_subdirectory="../Docs/logs"):
    """
    Sets up a logger with both console and file handlers,
    using a dynamic file name based on timestamp in a subdirectory.
    """
    logger = logging.getLogger('fleetserverapi')
    logger.setLevel(logging.DEBUG) 
    if not logger.handlers:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir_path = os.path.join(script_dir, log_subdirectory)
        os.makedirs(log_dir_path, exist_ok=True)
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name = f"fleetserverapi_{timestamp_str}.log"
        log_file_path = os.path.join(log_dir_path, log_file_name)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG) # File sees DEBUG and above (more detail)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    return logger
