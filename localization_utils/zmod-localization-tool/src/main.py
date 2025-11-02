import os
import re
import yaml
from string_extractor import extract_localizable_strings
from config_parser import write_localization_file

def process_cfg_files(directory):
    localization_data = {}

    for filename in os.listdir(directory):
        if filename.endswith('.cfg'):
            file_path = os.path.join(directory, filename)
            strings = extract_localizable_strings(file_path)
            localization_data.update(strings)

    return localization_data

def generate_unique_key(string):
    return re.sub(r'\W+', '_', string).lower()

if __name__ == "__main__":
    # Určit cestu relativně k umístění skriptu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..', 'orig'))
    en_dir = os.path.join(base_dir, 'en')
    
    print(f"Script directory: {script_dir}")
    print(f"Base directory: {base_dir}")
    print(f"English directory: {en_dir}")
    print(f"Directory exists: {os.path.exists(en_dir)}")
    
    if os.path.exists(en_dir):
        cfg_files = [f for f in os.listdir(en_dir) if f.endswith('.cfg')]
        print(f"Found {len(cfg_files)} .cfg files: {cfg_files}")
    
    result = write_localization_file(base_dir=base_dir, en_dir=en_dir)
    
    if result:
        print(f"Localization file created: {result}")
    else:
        print("No .cfg files found to process")