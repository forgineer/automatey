import importlib
import os
import sys
import tempfile
import types
import unittest

from click.testing import CliRunner

import automatey.duck_tools as duck_tools


class TestCombineCSVFiles(unittest.TestCase):
	def _write_csv(self, path: str, rows: list[str]):
		with open(path, 'w', newline='') as fh:
			fh.write('\n'.join(rows))

	def test_combine_csv_files_function_removes_duplicates_by_default(self):
		# Create a temporary directory with two CSV files where one row is duplicated
		with tempfile.TemporaryDirectory() as td:
			file1 = os.path.join(td, 'mock_data1.csv')
			file2 = os.path.join(td, 'mock_data2.csv')

			# header + two rows
			rows1 = ['id,name', '1,A', '2,B']
			# header + duplicate row 2,B and a new row 3,C
			rows2 = ['id,name', '2,B', '3,C']

			self._write_csv(file1, rows1)
			self._write_csv(file2, rows2)

			# Run the function directly (default all=False should use UNION BY NAME)
			duck_tools.combine_csv_files(directory_path=td, output_file='combined.csv', all=False)

			combined = os.path.join(td, 'combined.csv')
			self.assertTrue(os.path.exists(combined), 'Combined CSV was not created')

			with open(combined, 'r', newline='') as fh:
				lines = [ln.strip() for ln in fh.read().splitlines() if ln.strip()]

			# Header plus rows; duplicates should be removed -> rows: 1,A ; 2,B ; 3,C
			self.assertGreaterEqual(len(lines), 1)
			header = lines[0]
			self.assertEqual(header, 'id,name')

			data_rows = lines[1:]
			self.assertEqual(len(data_rows), 3)
			self.assertIn('1,A', data_rows)
			self.assertIn('2,B', data_rows)
			self.assertIn('3,C', data_rows)

	def test_cli_runner_all_option_keeps_duplicates(self):
		# Prepare a fake module at import-time so importing automatey.cli succeeds
		fake_name = 'automatey.data_tools'
		fake_module = types.ModuleType(fake_name)
		fake_module.combine_csv_files = duck_tools.combine_csv_files

		# Insert the fake module into sys.modules before importing the CLI
		sys.modules[fake_name] = fake_module
		try:
			# Import the CLI module (it imports combine_csv_files from automatey.data_tools)
			import automatey.cli as cli
			importlib.reload(cli)

			runner = CliRunner()

			# Use an isolated filesystem for the CLI run so current directory is our test dir
			with runner.isolated_filesystem():
				# create CSV files in the current working directory
				with open('mock_data1.csv', 'w', newline='') as fh:
					fh.write('\n'.join(['id,name', '1,A', '2,B']))

				with open('mock_data2.CSV', 'w', newline='') as fh:
					# use uppercase extension to ensure glob is case-sensitive on some platforms
					fh.write('\n'.join(['id,name', '2,B', '3,C']))

				# Invoke CLI with --all to retain duplicates (UNION ALL BY NAME)
				result = runner.invoke(cli.combine_csv_files_command, ['--all'])
				self.assertEqual(result.exit_code, 0, msg=result.output)

				combined = os.path.join(os.getcwd(), 'combined.csv')
				self.assertTrue(os.path.exists(combined), 'Combined CSV was not created by CLI')

				with open(combined, 'r', newline='') as fh:
					lines = [ln.strip() for ln in fh.read().splitlines() if ln.strip()]

				# Header plus rows; duplicates should be preserved -> rows: 1,A ; 2,B ; 2,B ; 3,C
				self.assertGreaterEqual(len(lines), 1)
				header = lines[0]
				self.assertEqual(header, 'id,name')

				data_rows = lines[1:]
				self.assertEqual(len(data_rows), 4)
				# Check duplicate exists
				self.assertEqual([r for r in data_rows if r == '2,B'].__len__(), 2)

		finally:
			# Clean up the fake module to avoid leaking into other tests
			if fake_name in sys.modules:
				del sys.modules[fake_name]


if __name__ == '__main__':
	unittest.main()

