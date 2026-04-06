import sys
import time
import logging
import __main__
import datetime
import functools

from pathlib import Path
from logging import FileHandler
from types import TracebackType
from typing import Any, Callable, Dict, Type, TypeVar, cast

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import Traceback

F = TypeVar('F', bound=Callable[..., Any])


class FormatoHibridoRich(logging.Formatter):
    def __init__(self, fmt: str):
        super().__init__(fmt)
        self.console: Console = Console(color_system=None, width=120)

    def format(self, record: logging.LogRecord) -> str:
        exc_info = record.exc_info
        record.exc_info = None
        
        texto_formatado = super().format(record)
        
        with self.console.capture() as capture:
            self.console.print(texto_formatado, markup=True)
            if exc_info and exc_info[0] is not None:
                tb = Traceback.from_exception(
                    exc_type  = exc_info[0],
                    exc_value = exc_info[1],
                    traceback = exc_info[2],
                    show_locals=True,
                    width=120
                )
                self.console.print(tb)

        record.exc_info = exc_info
        return capture.get().rstrip('\n')


class HandleLog:
    _shared_state: Dict[str, Any] = {}

    def __init__(self, file_log: bool, name: str = "example"):
        self.__dict__ = self._shared_state

        if not hasattr(self, 'is_initialized'):
            self.keep_logs_for_days: int = 7
            
            self.file_log: bool = file_log
            self.name    : str  = name
            
            self.logger = logging.getLogger(f"{self.name}")
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False

            if self.logger.hasHandlers():
                self.logger.handlers.clear()

            self.base_fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            
            console_handler = RichHandler(
                level                  = logging.INFO,
                show_path              = True,
                rich_tracebacks        = True,
                tracebacks_show_locals = True,
                markup                 = True,
            )
            
            self.rich_formatter = FormatoHibridoRich(fmt=self.base_fmt)
            self.logger.addHandler(console_handler)
    
            sys.excepthook = self._excepthook
            self.clear_logs()
            
            self.is_initialized = True
            self.setup_file_logging()

    def setup_file_logging(self) -> None:
        if self.file_log:
            now: str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')            
            self.file_name = f"LOG_{self.name}/{now}.log"
            
            log_path = Path(self.file_name)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = FileHandler(
                filename = self.file_name, 
                encoding = "utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self.rich_formatter)
            self.logger.addHandler(file_handler)
    
    def change_keep_log(self, days: int) -> None:
        self.keep_logs_for_days = days
        self.clear_logs()

    def __repr__(self) -> str:
        return f"HandleLog(name={self.logger.name})"
    
    def clear_logs(self) -> None:
        log_dir = Path(f"LOG_{self.name}")
        if log_dir.exists() and log_dir.is_dir():
            for log_file in log_dir.glob("*.log"):
                if log_file.is_file():
                    file_age = time.time() - log_file.stat().st_mtime
                    if file_age > self.keep_logs_for_days * 24 * 60 * 60:  
                        try:
                            log_file.unlink()
                            self.logger.info(f"Deleted old log file: {log_file.name}")
                        except Exception as e:
                            self.logger.error(f"Failed to delete log file {log_file.name}: {e}")

    def _excepthook(
            self, 
            exc_type     : Type[BaseException], 
            exc_value    : BaseException,
            exc_traceback: TracebackType
        ) -> None:
        self.logger.critical(
            "A fatal error has occurred! Unhandled exception details:", 
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    def flow(self, func: F) -> F: 
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.logger.debug(f"[FLOW IN] '{func.__name__}' running with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            self.logger.debug(f"[FLOW OUT] '{func.__name__}' returned results: {result}")
            return result
        return cast(F, wrapper)

    def time(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            result     = func(*args, **kwargs)
            end_time   = time.perf_counter()
            self.logger.debug(f"[TIMER] '{func.__name__}' executed in {end_time - start_time:.6f} seconds.")
            return result
        return cast(F, wrapper)

    def deactivate(self) -> None:
        self.logger.setLevel(logging.CRITICAL + 1)
        self.logger.info("Logging deactivated. No further messages will be logged.")

    def activate(self) -> None:
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Logging activated. All messages will be logged.")

    def deactivate_console(self) -> None:
        for handler in self.logger.handlers:
            if isinstance(handler, RichHandler):
                self.logger.removeHandler(handler)
                self.logger.info("Console logging deactivated.")
                break

    def activate_console(self) -> None:
        if not any(isinstance(handler, RichHandler) for handler in self.logger.handlers):
            console_handler = RichHandler(
                level                  = logging.INFO,
                show_path              = True,
                rich_tracebacks        = True,
                tracebacks_show_locals = True,
                markup                 = True,
            )
            self.logger.addHandler(console_handler)
            self.logger.info("Console logging activated.")

    def deactivate_file(self) -> None:
        self.file_log = False
        for handler in self.logger.handlers:
            if isinstance(handler, FileHandler):
                self.logger.removeHandler(handler)
                self.logger.info("File logging deactivated.")
                break

    def activate_file(self) -> None:   
        self.file_log = True
        self.setup_file_logging()
        self.logger.info("File logging activated.")

    def _format_string(self, *args, **kwargs) -> str:
        msg = " ".join(str(arg) for arg in args)
        msg_kwargs = " | ".join(f"{key}={value}" for key, value in kwargs.items())

        if msg and msg_kwargs:
            return f"{msg} | {msg_kwargs}"
        return msg or msg_kwargs

    def info(self, *args, **kwargs) -> None:
        msg = self._format_string(*args, **kwargs)
        self.logger.info(msg, stacklevel=2)
    
    def debug(self, *args, **kwargs) -> None:
        msg = self._format_string(*args, **kwargs)
        self.logger.debug(msg, stacklevel=2)

    def warning(self, *args, **kwargs) -> None:
        msg = self._format_string(*args, **kwargs)
        self.logger.warning(msg, stacklevel=2)

    def error(self, *args, **kwargs) -> None:
        msg = self._format_string(*args, **kwargs)
        self.logger.error(msg, stacklevel=2)

    def critical(self, *args, **kwargs) -> None:
        msg = self._format_string(*args, **kwargs)
        self.logger.critical(msg, stacklevel=2)

    def exception(self, *args, **kwargs) -> None:
        msg = self._format_string(*args, **kwargs)
        self.logger.exception(msg, stacklevel=2)


if __name__ == "__main__":        
    log = HandleLog(file_log=False, name="robot_arm")
    
    log.info("Sending joint coordinates over TCP...")
    log.warning("Coordinates received. Actuators engaging.")
    log.info("Attempting to close gripper...")

    @log.flow
    def teste_flow(a: int, b: int) -> int:
        return a + b

    @log.time
    def teste_time(x: int) -> str:
        for _ in range(x):
            time.sleep(1)
        return f"Finished | {x} seconds."

    log.debug([1, 2, 3, 4, 5, 6])

    #raise RuntimeError("Collision detected on axis 6!")