def extract_localizable_strings(cfg_file_path):
    localizable_strings = {}
    with open(cfg_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if 'RESPOND' in line and 'MSG="' in line:
                start_index = line.find('MSG="') + 5
                end_index = line.find('"', start_index)
                if end_index != -1:
                    message = line[start_index:end_index]
                    key = generate_unique_key(message, localizable_strings)
                    localizable_strings[key] = message
    return localizable_strings

def generate_unique_key(message, existing_keys):
    base_key = message.lower().replace(' ', '_').replace('"', '').replace("'", '')
    key = base_key
    counter = 1
    while key in existing_keys:
        key = f"{base_key}_{counter}"
        counter += 1
    return key

def process_cfg_files_in_directory(directory):
    import os
    all_localizable_strings = {}
    for filename in os.listdir(directory):
        if filename.endswith('.cfg'):
            file_path = os.path.join(directory, filename)
            localizable_strings = extract_localizable_strings(file_path)
            all_localizable_strings.update(localizable_strings)
    return all_localizable_strings

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python string_extractor.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]
    localizable_strings = process_cfg_files_in_directory(directory_path)
    for key, message in localizable_strings.items():
        print(f"{key}: {message}")