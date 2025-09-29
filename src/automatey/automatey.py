import atexit
import logging
import os
import time
import tomllib

from datetime import datetime, timedelta
from logging.config import dictConfig
from pathlib import Path
from typing import Any


class Automatey:
    """
    This is the main Automatey module. It contains all the core functionality and classes for the Automatey package.
    """
    # Singleton instance variable
    _instance = None

    # Start time of script in seconds (for exit time later)
    _start_time: float = time.time()

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern implementation to ensure only one instance of Automatey exists.
        """
        if cls._instance is None:
            cls._instance = super(Automatey, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                 config_file_path: str = 'automatey.toml',
                 configure_logging: bool = True,
                 register_atexit_timer: bool = True) -> None:
        """
        The constructor for the Automatey class.

        :param configure_logging: A boolean value indicating whether to configure logging.
        :param register_atexit_timer: A boolean value indicating whether to register the atexit timer.
        :return: None
        """
        # Prevent re-initialization in singleton pattern
        if getattr(self, '_initialized', False):
            return
        
        # Mark as initialized (for singleton pattern)
        self._initialized = True

        # Datetime Constant
        self._current_date_time: datetime = datetime.now()

        # Date Constants
        self._current_year: str = str(self._current_date_time.year)
        self._current_month: str = str(self._current_date_time.month).rjust(2, '0')
        self._current_day: str = str(self._current_date_time.day).rjust(2, '0')
        self._current_date: str = self._current_year + self._current_month + self._current_day

        # Time Constants (not meant to be accessed outside the class)
        self._current_hour: str = str(self._current_date_time.hour).rjust(2, '0')
        self._current_minute: str = str(self._current_date_time.minute).rjust(2, '0')
        self._current_second: str = str(self._current_date_time.second).rjust(2, '0')
        self._current_time: str = self._current_hour + self._current_minute + self._current_second

        # Config file location (found by set_config method)
        self.config_location: str = ''

        # Initialize config and core constants
        self.config: dict = self.set_config(config_file_path)

        if configure_logging:
            self.configure_logging()
        
        if register_atexit_timer:
            self.register_atexit_timer()

    def set_config(self, 
                   config_file_path: str) -> dict:
        """
        Searches for the configuration file by walking up the directory tree from the current working directory. 
        If an absolute path is provided, it attempts to load the configuration from that path directly.
        
        :param config_file_path: The name or absolute path of the configuration file to search for.
        :return: The loaded configuration as a dictionary.
        """
        # Check if the provided path is absolute first if a configuration file was provided by the user.
        if os.path.isabs(config_file_path):
            try:
                with open(config_file_path, "rb") as f:
                    config = tomllib.load(f)
                    self.config_location = config_file_path
                    return config
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"Malformed TOML in config file: {config_file_path}") from e
            except FileNotFoundError:
                raise FileNotFoundError(f"Configuration file '{config_file_path}' not found. Please provide a valid path.")

        # If not absolute, walk up the directory tree to find the config file by name
        current_dir = Path(os.getcwd()).resolve()
        root_dir = current_dir.anchor  # e.g., 'C:\' or '/' depending on OS
        config_path = None

        while True:
            candidate = current_dir / config_file_path

            if candidate.exists():
                config_path = candidate
                self.config_location = str(config_path)
                break
            
            if str(current_dir) == root_dir:
                break

            current_dir = current_dir.parent

        if config_path is None:
            raise FileNotFoundError(f"Configuration file '{config_file_path}' not found. Please create one in the current directory or any parent directory or provide a valid path.")

        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
                return config
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Malformed TOML in config file: {config_path}") from e

    def get_config(self, *keys) -> Any:
        """
        Retrieve a nested configuration value from the 'config' dictionary using a sequence of keys.

        :param keys: A sequence of keys to walk down the 'config' dictionary.
        :return: The value at the nested key path, or None if any key is missing.
        """
        value: dict = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def configure_logging(self) -> None:
        """
        This method initializes the logging configuration for the Automatey package.

        Sample configuration in automatey.toml:
        [automatey.logging]
        enable_file_handler = true
        filename = "./Log/automatey_<YYYY><MM><DD>.log"
        filemode = "a"
        format = "%(asctime)s: %(levelname)s: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        encoding = "utf-8"
        level = "INFO"
        
        :return: None
        """
        # Logging Constants
        logging_format: str = self.get_config('automatey', 'logging', 'format') or "%(asctime)s: %(levelname)s: %(message)s"
        logging_datefmt: str = self.get_config('automatey', 'logging', 'datefmt') or "%Y-%m-%d %H:%M:%S"
        logging_encoding: str = self.get_config('automatey', 'logging', 'encoding') or "utf-8"
        logging_level: str = self.get_config('automatey', 'logging', 'level') or "INFO"

        # Define base logging configuration
        logging_config: dict = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": logging_format,
                    "datefmt": logging_datefmt,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": logging_level,
                    "stream": "ext://sys.stdout",
                }
            }
        }
        
        # Define file handler defaults
        enable_file_handler: bool = self.get_config('automatey', 'logging', 'enable_file_handler')
        
        if enable_file_handler is not False:
            logging_filename: str = self.get_config('automatey', 'logging', 'filename') or './Log/automatey_<DATE>.log'
            logging_filemode: str = self.get_config('automatey', 'logging', 'filemode') or "a"

            # Create parent directory path if it doesn't already exist
            file_directory, file_name = os.path.split(logging_filename)
            Path(file_directory).mkdir(parents=True, exist_ok=True)

            # Replace datetime format variables in filename
            logging_filename = logging_filename.replace("<YYYY>", self._current_year)
            logging_filename = logging_filename.replace("<MM>", self._current_month)
            logging_filename = logging_filename.replace("<DD>", self._current_day)
            logging_filename = logging_filename.replace("<hh>", self._current_hour)
            logging_filename = logging_filename.replace("<mm>", self._current_minute)
            logging_filename = logging_filename.replace("<ss>", self._current_second)
            logging_filename = logging_filename.replace("<DATE>", self._current_date)
            logging_filename = logging_filename.replace("<TIME>", self._current_time)

            # Add file handler to logging configuration
            logging_config['handlers']['file'] = {
                "class": "logging.FileHandler",
                "formatter": "default",
                "level": logging_level,
                "filename": logging_filename,
                "mode": logging_filemode,
                "encoding": logging_encoding,
            }

        # Define 'automatey' logger to use both console and file handlers if file handler is enabled
        if enable_file_handler:
            logging_config['loggers'] = {
                'automatey': {
                    'handlers': ['console', 'file'],
                    'level': logging_level,
                    'propagate': False
                }
            }
        else:
            logging_config['loggers'] = {
                'automatey': {
                    'handlers': ['console'],
                    'level': logging_level,
                    'propagate': False
                }
            }

        # Configure logging
        dictConfig(logging_config)

    @property
    def logger(self) -> logging.Logger:
        """
        Returns the logger instance for the Automatey package.
        :return: The logger instance.
        """
        return logging.getLogger("automatey")

    def register_atexit_timer(self) -> None:
        """
        Registers an atexit function to log the script's execution time upon exit.
        """
        @atexit.register
        def exit_timer():
            end_time: float = time.time() - self._start_time
            td_end_time_str: str = str(timedelta(seconds=end_time))
            self.logger.info(f'All tasks complete: {td_end_time_str}')
