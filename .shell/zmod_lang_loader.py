import yaml
import os
import logging
import sys

# Konfigurace loggingu
LOG_LEVEL = os.getenv("ZMOD_LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("ZMOD_LOG_FILE", "/tmp/zmod_lang_loader.log")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
LANG_PATH = "/root/printer_data/config/mod/language.yml"

try:
    logger.debug(f"Loading language from file: {LANG_PATH}")
    
    if not os.path.exists(LANG_PATH):
        logger.error(f"Language file not found: {LANG_PATH}")
        raise FileNotFoundError(f"Language file not found: {LANG_PATH}")
    
    with open(LANG_PATH, "r", encoding="utf-8") as f:
        translations = yaml.safe_load(f)
    
    if translations is None:
        logger.warning(f"Language file is empty or invalid: {LANG_PATH}")
        translations = {}
    
    logger.info(f"Language successfully loaded. Number of items: {len(translations)}")
    logger.debug(f"Available keys: {list(translations.keys())[:10]}...")  # First 10 keys

except FileNotFoundError as e:
    logger.error(f"Language file not found: {e}")
    translations = {}
except yaml.YAMLError as e:
    logger.error(f"Error parsing YAML: {e}")
    translations = {}
except Exception as e:
    logger.error(f"Unexpected error loading language: {e}", exc_info=True)
    translations = {}


def t(key: str, **kwargs):
    """
    Returns the translated text for the given key with formatting support.

    Args:
        key: Translation key (e.g. MSG_START_PRINT)
        **kwargs: Formatting arguments (e.g. temp=210)
    
    Returns:
        Translated text or original key if translation was not found
    """
    try:
        if key not in translations:
            logger.warning(f"Translation not found for key: {key}")
            return key
        
        text = translations[key]
        logger.debug(f"Loaded translation for key '{key}': {text[:50]}...")

        if not kwargs:
            logger.debug(f"Returning text without formatting for key: {key}")
            return text
        
        # Formátování textu se zadanými argumenty
        formatted_text = text.format(**kwargs)
        logger.debug(f"Formatted text for key '{key}' with arguments{list(kwargs.keys())}: {formatted_text[:50]}...")
        return formatted_text
        
    except KeyError as e:
        logger.error(f"Formatting error: Unknown variable {e} for key '{key}'")
        logger.error(f"Text: {text}, Available arguments: {list(kwargs.keys())}")
        return text  # Returns text without formatting

    except Exception as e:
        logger.error(f"Unexpected error in t() for key '{key}': {e}", exc_info=True)
        return key
