import unittest
from src.localization_manager import LocalizationManager

class TestLocalizationManager(unittest.TestCase):

    def setUp(self):
        self.manager = LocalizationManager()

    def test_extract_localizable_strings(self):
        cfg_content = '''
        RESPOND PREFIX="info" MSG="Loading filament {prutok} {filament_type}"
        RESPOND PREFIX="error" MSG="Filament jam detected (IFS)."
        RESPOND PREFIX="info" MSG="Filament runout detected (IFS). Use RESUME_MOTION_SENSOR to resume printing after the filament in the extruder runs out."
        '''
        expected_strings = [
            "Loading filament {prutok} {filament_type}",
            "Filament jam detected (IFS).",
            "Filament runout detected (IFS). Use RESUME_MOTION_SENSOR to resume printing after the filament in the extruder runs out."
        ]
        extracted_strings = self.manager.extract_localizable_strings(cfg_content)
        self.assertEqual(extracted_strings, expected_strings)

    def test_generate_unique_keys(self):
        strings = [
            "Loading filament {prutok} {filament_type}",
            "Filament jam detected (IFS)."
        ]
        expected_keys = [
            "loading_filament_{prutok}_{filament_type}",
            "filament_jam_detected_ifs"
        ]
        generated_keys = self.manager.generate_unique_keys(strings)
        self.assertEqual(generated_keys, expected_keys)

    def test_localization_process(self):
        # Mock the necessary methods and data for testing the localization process
        self.manager.load_configurations = lambda: None
        self.manager.save_localization_file = lambda: None
        self.manager.extract_localizable_strings = lambda x: [
            "Test message 1",
            "Test message 2"
        ]
        self.manager.generate_unique_keys = lambda x: [
            "test_message_1",
            "test_message_2"
        ]
        
        self.manager.process_localization()
        self.assertTrue(self.manager.localization_data)
        self.assertIn("test_message_1", self.manager.localization_data)
        self.assertIn("test_message_2", self.manager.localization_data)

if __name__ == '__main__':
    unittest.main()