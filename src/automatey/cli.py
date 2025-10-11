import click

from . import __version__
from graphlib import TopologicalSorter


@click.command()
@click.option('--version', is_flag=True, help='Prints the version of the package.')
@click.option('--run', is_flag=True, help='Executes the DAG if one is provided.')
@click.option('--config', default='automatey.toml', help='Absolute path or name of the configuration file.')
@click.option('--disable_logging', is_flag=True, help='Disables logging during execution.')
@click.option('--disable_exit_timer', is_flag=True, help='Disables the exit timer for execution.')
@click.option('--max_workers', default=1, help='The maximum number of workers to use for parallel tasks.')
@click.option('--ui', is_flag=True, help='Starts the user interface.')
def main(version: bool, run: bool, config: str, disable_logging: bool, disable_exit_timer: bool, max_workers: int, ui: bool) -> None:
    if version:
        click.echo(f'Automatey Version: {__version__}')

    elif ui:
        click.echo('This feature is coming soon!')
    
    elif run:
        # Import and initialize Automatey for running tasks
        from . import Automatey

        _automatey = Automatey(config_file_path=config,
                               configure_logging=not disable_logging,
                               configure_exit_timer=not disable_exit_timer)
    
        # Attempt to retrieve the DAG from the configuration
        try:
            # Retrieve the DAG from the configuration
            dag: dict = _automatey.get_config('automatey', 'dag')

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


if __name__ == '__main__':
    main()
