import sys
import traceback
import datetime
import time
import logging
import __main__
import functools
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, Type, TypeVar, cast
from types import TracebackType

from rich.logging import RichHandler

F = TypeVar('F', bound=Callable[..., Any])

class HandleDebug:
    _shared_state: Dict[str, Any] = {}

    def __init__(self, name: str = "example"):
        self.__dict__ = self._shared_state
        
        filename = __main__.__file__.split("/")[-1].split(".")[0]
        name = filename if filename != "__main__" else name

        if not hasattr(self, 'is_initialized'):
            now: str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')            
            file_name = f"LOG_{name}/{now}.log"

            log_path = Path(file_name)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            self.logger = logging.getLogger(f"{name}")
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False

            if self.logger.hasHandlers():
                self.logger.handlers.clear()

            fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

            console_handler = RichHandler(
                level=logging.INFO,
                show_path=True,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                markup=True,
            )

            file_handler = RotatingFileHandler(
                filename=file_name, 
                maxBytes=5 * 1024 * 1024, 
                backupCount=3,            
                encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(fmt)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            sys.excepthook = self._excepthook
            
            self.is_initialized = True


    def __repr__(self) -> str:
        return f"HandleDebug(name={self.logger.name})"


    def _excepthook(
            self, 
            exc_type: Type[BaseException], 
            exc_value: BaseException,
            exc_traceback: TracebackType
        ) -> None:

        self.logger.critical("A fatal error has occurred! Unhandled exception details:")
        self.logger.exception("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    

    def flow(self, func: F) -> F: 
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.logger.debug(f"[FLOW IN]'{func.__name__}' running with args={args}, kwargs={kwargs}")
        
            result = func(*args, **kwargs)
            self.logger.debug(f"[FLOW OUT]'{func.__name__}' returned results: {result}")
            return result
        
        return cast(F, wrapper)


    def time(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            self.logger.debug(f"[TIMER] '{func.__name__}' executed in {end_time - start_time:.6f} seconds.")
            
            return result
        return cast(F, wrapper)


    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)   

    def exception(self, message: str) -> None:
        self.logger.exception(message)  

log = HandleDebug()

if __name__ == "__main__":        
    log.info("Sending joint coordinates over TCP...")
    log.warning("Coordinates received. Actuators engaging.")
    log.info("Attempting to close gripper...")

    @log.flow
    def teste_flow(a: int, b: int) -> int:
        return a + b

    @log.time
    def teste_time(x: int) -> str:
        for i in range(x):
            time.sleep(1)
        return f"Finished | {x} seconds."
    
    log.warning(teste_time(2))

    #raise RuntimeError("Collision detected on axis 6!")
