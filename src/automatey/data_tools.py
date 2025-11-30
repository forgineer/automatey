import click
import duckdb
import glob
import os


def combine_csv_files(directory_path: str = None, output_file: str = 'combined.csv', all: bool = False) -> None:
    """
    Combines all CSV files in the specified directory into a single CSV file. If no directory is specified,
    the current working directory is used.

    :param directory_path: The path to the directory containing CSV files.
    :param output_file: The name of the output combined CSV file.
    """
    if directory_path is None:
        directory_path = '.'

    # Find all CSV files in the specified directory
    csv_files: list = glob.glob(os.path.join(directory_path, '*.csv'))
    #csv_files.extend(glob.glob(os.path.join(directory_path, '*.CSV')))

    # Define SQL statements
    sql_statements: list = []

    if not csv_files:
        click.echo(f'No CSV files found in directory: {directory_path}')
        return

    if len(csv_files) > 1:
        click.echo(f'Found {len(csv_files)} CSV files to combine.')
        click.echo('CSV Files:')
        for idx, file in enumerate(csv_files):
            click.echo(f' - {file}')

            if idx > 0:
                if not all:
                    sql_statements.append("UNION BY NAME")
                else:
                    sql_statements.append("UNION ALL BY NAME")
            
            sql_statements.append(f"SELECT * FROM read_csv_auto('{file}', header=True)")

        click.echo(f'Combining CSV files into: {os.path.join(directory_path, output_file)}')
    else:
        click.echo('Only one CSV file found. There is no point to combining a single file.')
        return

    sql_statements_str: str = '\n'.join(sql_statements)
    click.echo(f'SQL Statement:\n{sql_statements_str}')

    # Create a DuckDB connection
    con = duckdb.connect(database=':memory:')

    # Use DuckDB to read and combine CSV files and retain headers for all files
    statement: str = f"""
    COPY (
        {sql_statements_str}
    ) TO '{os.path.join(directory_path, output_file)}' WITH (HEADER TRUE);
    """

    con.execute(statement)
    con.close()
