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


def split_csv_file(input_file: str, output_directory: str = None, chunk_size: int = 1000) -> None:
    """
    Splits a large CSV file into smaller chunks.

    :param input_file: The path to the input CSV file.
    :param output_directory: The directory where the split files will be saved.
    :param chunk_size: The number of rows per split file.
    """
    if output_directory is None:
        output_directory = os.path.dirname(input_file)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Create a DuckDB connection
    con = duckdb.connect(database=':memory:')

    # Read the input CSV file
    con.execute(f"CREATE TABLE temp AS SELECT * FROM read_csv_auto('{input_file}', header=True);")

    # Get total number of rows
    total_rows = con.execute("SELECT COUNT(*) FROM temp;").fetchone()[0]

    # Split the CSV file into chunks
    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        output_file = os.path.join(output_directory, f'split_{start // chunk_size + 1}.csv')

        con.execute(f"""
        COPY (
            SELECT * FROM temp
            LIMIT {chunk_size} OFFSET {start}
        ) TO '{output_file}' WITH (HEADER TRUE);
        """)

        click.echo(f'Created split file: {output_file}')

    con.close()