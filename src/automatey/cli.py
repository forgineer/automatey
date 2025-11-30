import click
import itertools
import threading
import time

from . import __version__
from .data_tools import combine_csv_files


class Spinner:
    """
    A simple console spinner usable as a context manager.

    Usage:
        with Spinner('Working...'):
            do_long_task()

    The spinner runs in a background thread and stops when the context exits.
    """
    def __init__(self, message="Working...", delay=0.1):
        self.message = message
        self.delay = delay
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        for ch in itertools.cycle("|/-\\"):
            if self._stop.is_set():
                break
            print(f"\r{self.message} {ch}", end="", flush=True)
            time.sleep(self.delay)
        # clear the line when done
        print("\r" + " " * (len(self.message) + 2) + "\r", end="", flush=True)

    def __enter__(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        # Do not swallow exceptions
        return False


@click.command()
@click.option('--version', is_flag=True, help='Prints the version of the package.')
@click.option('--run', is_flag=True, help='Executes the DAG if one is provided.')
@click.option('--config', default='automatey.toml', help='Absolute path or name of the configuration file.')
@click.option('--disable_logging', is_flag=True, help='Disables logging during execution.')
@click.option('--disable_exit_timer', is_flag=True, help='Disables the exit timer for execution.')
@click.option('--max_workers', default=1, help='The maximum number of workers to use for parallel tasks.')
def automatey_command(version: bool, run: bool, config: str, disable_logging: bool, disable_exit_timer: bool, max_workers: int) -> None:
    if version:
        click.echo(f'Automatey Version: {__version__}')
    
    elif run:
        # Import and initialize Automatey for running tasks
        from . import Automatey

        _a = Automatey(config_file_path=config,
                       configure_logging=not disable_logging,
                       configure_exit_timer=not disable_exit_timer)
    
        # Attempt to retrieve the DAG from the configuration
        try:
            # Retrieve the DAG from the configuration
            dag: dict = _a.get_config('automatey', 'dag')

            if dag is None:
                click.echo('No DAG found in the configuration file.')
                return
            
            # Retrieve tasks within the DAG (if any)
            tasks: list = dag.get('tasks', [])
            
            for task in tasks:
                if 'dependencies' not in task:
                    task['dependencies'] = []

        except KeyError:
            click.echo('No DAG found in the configuration file.')
            return
    else:
        click.echo('No action specified. Use --help for more information.')


@click.command()
@click.option('--all', is_flag=True, help='Ensures all rows are included when combining CSV files. Duplicates are not removed.')
def combine_csv_files_command(all: bool = False) -> None:
    combine_csv_files(all=all)
