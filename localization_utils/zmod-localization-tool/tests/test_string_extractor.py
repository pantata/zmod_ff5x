import unittest
from src.string_extractor import extract_localizable_strings

class TestStringExtractor(unittest.TestCase):

    def test_extract_localizable_strings(self):
        test_input = '''
        [module]
        RESPOND TYPE=info MSG="This is a test message."
        RESPOND TYPE=error MSG="An error occurred."
        RESPOND PREFIX=info MSG="Another informational message."
        '''
        expected_output = {
            "test_message_1": "This is a test message.",
            "test_message_2": "An error occurred.",
            "test_message_3": "Another informational message."
        }
        result = extract_localizable_strings(test_input)
        self.assertEqual(result, expected_output)

    def test_no_localizable_strings(self):
        test_input = '''
        [module]
        Some random text without any RESPOND statements.
        '''
        expected_output = {}
        result = extract_localizable_strings(test_input)
        self.assertEqual(result, expected_output)

    def test_multiple_responses(self):
        test_input = '''
        [module]
        RESPOND TYPE=info MSG="First message."
        RESPOND TYPE=info MSG="Second message."
        RESPOND TYPE=info MSG="Third message."
        '''
        expected_output = {
            "test_message_1": "First message.",
            "test_message_2": "Second message.",
            "test_message_3": "Third message."
        }
        result = extract_localizable_strings(test_input)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()