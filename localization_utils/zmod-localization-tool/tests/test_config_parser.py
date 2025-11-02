import unittest
from src.config_parser import read_config, write_config

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        self.test_file = 'test_config.cfg'
        self.test_content = '[test_section]\nkey=value\n'

    def tearDown(self):
        import os
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_read_config(self):
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
        
        result = read_config(self.test_file)
        expected = {'test_section': {'key': 'value'}}
        self.assertEqual(result, expected)

    def test_write_config(self):
        config_data = {'test_section': {'key': 'value'}}
        write_config(self.test_file, config_data)

        with open(self.test_file, 'r') as f:
            content = f.read()
        
        expected_content = '[test_section]\nkey=value\n'
        self.assertEqual(content, expected_content)

    def test_write_empty_config(self):
        write_config(self.test_file, {})
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        
        expected_content = ''
        self.assertEqual(content, expected_content)

if __name__ == '__main__':
    unittest.main()