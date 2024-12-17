import unittest
import tempfile
import os
import sys
from unittest.mock import patch
from io import StringIO
from toml_converter import toml_to_custom


class TestTomlToCustom(unittest.TestCase):

    def setUp(self):
        self.test_output_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_output_file.close()

    def tearDown(self):
        if os.path.exists(self.test_output_file.name):
            os.remove(self.test_output_file.name)

    def run_conversion(self, input_data):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
                patch('sys.stdin', new_callable=StringIO) as mock_stdin:
            mock_stdin.write(input_data)
            mock_stdin.seek(0)
            toml_to_custom(mock_stdin.read(), self.test_output_file.name)
            return mock_stdout.getvalue()

    def test_basic_conversion(self):
        input_data = """
        name = "Test"
        version = 1
        description = "A simple test."
        """
        expected_output = """const name = 'Test';
const version = 1;
const description = 'A simple test.';
"""
        self.run_conversion(input_data)
        with open(self.test_output_file.name, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read().strip(), expected_output.strip())

    def test_expression_conversion(self):
        input_data = """
        x = 5
        y = 10
        result = ".abs(x - y)."
        """
        expected_output = """const x = 5;
const y = 10;
const result = 5;
"""
        self.run_conversion(input_data)
        with open(self.test_output_file.name, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read().strip(), expected_output.strip())



    def test_nested_dict(self):
        input_data = """
        settings = { theme = "dark", version = 2 }
        """
        expected_output = """const settings = {
    theme : 'dark',
    version : 2,
};
"""
        self.run_conversion(input_data)
        with open(self.test_output_file.name, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read().strip(), expected_output.strip())



    def test_conversion_with_empty_input(self):
        input_data = ""
        expected_output = ""
        self.run_conversion(input_data)
        with open(self.test_output_file.name, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read().strip(), expected_output.strip())

    def test_conversion_to_file(self):
        input_data = """
        name = "Test Name"
        version = 2
        """
        self.run_conversion(input_data)
        with open(self.test_output_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("const name = 'Test Name';", content)
            self.assertIn("const version = 2;", content)


if __name__ == '__main__':
    unittest.main()
