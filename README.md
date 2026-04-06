# 🛠️ Debug & Logging Handler

## 📝 Project Description

The **HandleDebug** module is a robust, rich-text-enabled logging utility designed for embedded software, robotics, and systems. It provides a drop-in replacement for standard print statements, offering dual-channel logging (console and file), automatic log rotation, execution timing, system flow tracing. By leveraging the `rich` library, it ensures high visibility for system state changes and hardware faults, making debugging complex state machines or TCP-controlled robotics significantly easier.

## 📦 Installation

This package is designed to be easily integrated into any Python project and can be installed directly via `pip`.

### Installation from Source (Git)

```bash
pip install git+https://github.com/Gabriel-br2/log.git
```

### Local Development Setup
If you want to modify the source code or contribute to the project, clone the repository and install it in editable mode:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gabriel-br2/log.git
   cd log
   ```

2. **Install in editable mode:**
   ```bash
   pip install -e .
   ```

## 🚀 Usage Example

Integrating **HandleDebug** into your codebase is straightforward. Since it uses a singleton-like pattern (Borg), you can initialize it in multiple files without duplicating handlers or log files.

### 1. Basic Initialization and Standard Logging

```python
from log import log

log.info("System booting up...")
log.debug("Checking connections on port 502...")
log.warning("Actuator on Axis 3 is running slightly hot.")
```

### 2. Advanced Message Formatting
The logger automatically merges multiple arguments and keyword arguments (`kwargs`), which is highly useful for dumping payloads or state variables without needing to write complex f-strings.

```python
sensor_data = [1.2, 3.4, 5.6, 7.8, 9.0, 1.1]

# Passing lists and kwargs directly
log.debug("Sensor Payload Received:", sensor_data, status="OK", latency_ms=12)
# Output: Sensor Payload Received: [1.2, 3.4, 5.6, 7.8, 9.0, 1.1] | status=OK | latency_ms=12
```

### 3. Profiling and Tracing with Decorators
Use the built-in decorators to automatically track the execution flow and measure performance—crucial for real-time control loops.

```python
import time

@log.flow
def calculate_kinematics(x: float, y: float) -> float:
    return (x ** 2) + (y ** 2)

@log.time
def move_to_home_position(delay_sec: int):
    log.info(f"Moving to home position, taking {delay_sec} seconds...")
    time.sleep(delay_sec)
    return "Home position reached."
```

### 4. Managing Log Retention
By default, the system keeps logs for 7 days. You can change this behavior at any time to save disk space on embedded devices (e.g., SD cards).

```python
# Change log retention policy to 3 days. 
# This immediately triggers a cleanup of older files.
log.change_keep_log(days=3)
```
   
## ⚙️ System Behavior

The system operates as a globally accessible singleton (via the Borg pattern), ensuring that all parts of the embedded application write to the exact same log context and file. 

* **Initialization:** Upon the first import, it automatically creates a log directory named after the executing script (e.g., `LOG_main/`) and generates a timestamped log file.
* **Automatic Log Rotation:** It scans the directory and deletes log files older than a specified number of days to prevent the embedded device from running out of storage.
* **Exception Hooking:** It overrides Python's default `sys.excepthook`. If a critical hardware fault or unhandled software exception occurs (e.g., a robotic collision), the system captures the full traceback, local variables, and logs it critically before crashing.
* **Dynamic Output Routing:** It allows developers to turn console and file logging on or off dynamically during runtime via method calls, which is useful for silencing logs during high-frequency polling loops.

## 📂 Code Structure
The codebase is structured into two primary classes and a set of utility decorators:

* **`HandleDebug` (Core Class):** The main logging manager. Handles assignment (File and Console), and provides standard logging methods (`info`, `debug`, `warning`, `error`, `critical`, `exception`).
* **`@flow` (Decorator):** Wraps functions to automatically log input arguments (`args`, `kwargs`) upon entry and the returned result upon exit.
* **`@time` (Decorator):** Wraps functions to measure and log their exact execution time using a high-resolution performance counter, crucial for real-time system profiling.

## 🛠️ Configuration Structure
The system is designed to be plug-and-play, but allows for the following runtime configurations:

* **Log Retention (`keep_logs_for_days`):** Configured via the `change_keep_log(days: int)` method. Defaults to 7 days.
* **Log Directory Name:** Automatically derived from the `__main__` execution file, but can be overridden by passing a `name` string to the `HandleDebug(name="custom_name")` constructor.
* **Runtime Toggles:** * `activate()` / `deactivate()`: Toggles the entire logging system.
    * `activate_console()` / `deactivate_console()`: Manages stdout printing.
    * `activate_file()` / `deactivate_file()`: Manages disk writes.

## 📌 Notes
* **Dependencies:** This module requires the `rich` library. Ensure you run `pip install rich` on your target hardware.
* **Global State:** Because it uses the Borg pattern (`self.__dict__ = self._shared_state`), you can instantiate `log = HandleDebug()` in multiple files, and they will all share the same configuration and file lock.

## ⚠️ Common Errors

| Error / Symptom | Possible Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'rich'` | The `rich` dependency is not installed on the system. | Run `pip install rich` or add it to `requirements.txt`. |
| `PermissionError: [Errno 13] Permission denied` | The script lacks privileges to create the `LOG_.../` directory. | Check OS folder permissions or run the script with appropriate user access (e.g., `sudo` if writing to protected paths). |
| Logs are missing from the console but appear in the file. | `log.deactivate_console()` was called in another module. | Ensure you call `log.activate_console()` if console visibility is required again. |

## 🏷️ Version
* **Current Version:** `1.0.0`
* **History:**
    * *v1.0.0* - Initial release.Rich tracebacks, log rotation, and flow/time decorators.

## 👥 Author
| Name | Role | Responsibilities |
| :--- | :--- | :--- |
| Gabriel-br2 | Automation Engineer | Core architecture, logging logic, hardware integration. | System Architect | Code review, testing on target hardware, documentation. |


> *"Debugging is like being the detective in a crime movie where you are also the murderer. Logs are your alibi."*
