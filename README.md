<p align="center">
  <img src="images/automatey_logo.png" alt="Automatey Logo" />
</p>

Automatey is a lightweight Python library designed to simplify the management of configurations and the execution of tasks as a Directed Acyclic Graph (DAG). It provides robust configuration handling, flexible logging, and utility features to streamline automation workflows.

## Features

- **Configuration Management**: Automatically discovers and loads configuration files (`automatey.toml`) from the current or parent directories.
- **Logging**: Configurable logging with support for both console and file handlers.
- **Singleton Design**: Ensures only one instance of the `Automatey` class is created during runtime.
- **Execution Timer**: Tracks and logs the total execution time of your script when it exits.

## Installation

Automatey is not yet published to PyPI, so you can clone this repository to use it locally:

```bash
git clone https://github.com/your-username/automatey.git
cd automatey
```

Ensure you are using Python 3.11 or later, as specified in the `.python-version` file.

## Usage

### Getting Started

1. **Initialize Automatey**:
   Import and create an instance of the `Automatey` class. This will automatically load the configuration file (`automatey.toml`) and set up logging.

   ```python
   from automatey import Automatey

   auto = Automatey()
   ```

2. **Access Configuration**:
   Use the `get_config` method to retrieve values from the loaded configuration.

   ```python
   # Example: Access the DAG name from the configuration
   dag_name = auto.get_config('automatey', 'dag', 'name')
   print(f"DAG Name: {dag_name}")
   ```

3. **Logging**:
   Automatey provides a pre-configured logger. Use it to log messages.

   ```python
   auto.logger.info("This is an info log message.")
   auto.logger.error("This is an error log message.")
   ```

4. **Execution Timer**:
   Automatey automatically logs the total execution time of your script when it exits.

### Configuration File

Automatey expects a `TOML` configuration file named `automatey.toml`. Here’s an example configuration:

```toml
foo = "bar"

[automatey.dag]
name = "ETL Pipeline"

[[automatey.dag.tasks]]
name = "extract"
depends_on = []

[[automatey.dag.tasks]]
name = "transform"
depends_on = ["extract"]

[[automatey.dag.tasks]]
name = "load"
depends_on = ["transform"]
```

### Logging Configuration

You can customize logging behavior in the `automatey.toml` file. For example:

```toml
[automatey.logging]
enable_file_handler = true
filename = "./Log/automatey_<YYYY><MM><DD>.log"
filemode = "a"
format = "%(asctime)s: %(levelname)s: %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
encoding = "utf-8"
level = "INFO"
```

- `enable_file_handler`: Enables logging to a file.
- `filename`: Specifies the log file name. You can use placeholders like `<YYYY>`, `<MM>`, `<DD>`, `<DATE>`, and `<TIME>` for dynamic filenames.
- `level`: Sets the logging level (e.g., `INFO`, `DEBUG`, `ERROR`).

### Example Script

Here’s a complete example of using Automatey:

```python
from automatey import Automatey

# Initialize Automatey
auto = Automatey()

# Access configuration
dag_name = auto.get_config('automatey', 'dag', 'name')
print(f"DAG Name: {dag_name}")

# Log messages
auto.logger.info("Starting the ETL pipeline...")
auto.logger.info(f"DAG Name: {dag_name}")
auto.logger.info("ETL pipeline completed successfully.")
```

## Project Structure

```
# Updated to specify language as plaintext
plaintext
automatey/
├── LICENSE
├── README.md
├── automatey.toml
├── pyproject.toml
├── src/
│   └── automatey/
│       ├── __init__.py
│       ├── automatey.py
│       ├── cli.py
│       └── ui.py
├── tests/
│   └── test_automatey.py
└── Log/
    ├── automatey_20250922.log
    └── automatey_20250928.log
```

## Testing

Automatey includes a basic test file in `tests/test_automatey.py`. To run the test:

```bash
python -m unittest discover tests
```

## Future Enhancements

- **Task Execution**: Extend Automatey to execute tasks defined in the DAG configuration.
- **CLI Support**: Implement a command-line interface for managing tasks.
- **UI Integration**: Build a user interface for visualizing and managing DAGs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
