# Zmod Localization Tool

## Overview
The Zmod Localization Tool is a Python-based utility designed to extract localizable strings from configuration files used in Klipper firmware. It processes `.cfg` files to identify strings that can be translated, generates unique localization keys, and manages the localization process across different languages.

## Features
- Extracts localizable strings in the format `RESPOND ... MSG="..."` from `.cfg` files.
- Generates unique keys for each extracted string for easy localization.
- Supports the creation of an `en.yml` file for English localization.
- Manages localization across multiple languages.
- Provides logging of changes made during the localization process.

## Project Structure
```
klipper-localization-tool
├── src
│   ├── main.py                # Entry point for the program
│   ├── config_parser.py       # Functions for reading and writing config files
│   ├── string_extractor.py     # Functions to extract localizable strings
│   └── localization_manager.py  # Manages the localization process
├── tests
│   ├── test_config_parser.py   # Unit tests for config_parser.py
│   ├── test_string_extractor.py # Unit tests for string_extractor.py
│   └── test_localization_manager.py # Unit tests for localization_manager.py
├── output
│   └── .gitkeep                # Keeps the output directory in version control
├── requirements.txt            # Lists project dependencies
├── .gitignore                  # Specifies files to ignore in Git
└── README.md                   # Documentation for the project
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd klipper-localization-tool
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the localization tool, execute the following command:
```
python src/main.py
```

This will process all `.cfg` files in the `orig/en` folder, extract localizable strings, and generate the necessary localization files.

## Testing
To run the unit tests, use the following command:
```
pytest tests/
```

This will execute all tests in the `tests` directory to ensure the functionality of the tool.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.