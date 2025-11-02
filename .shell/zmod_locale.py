
# (2025) ludek.slouf@gmail.com
# Zmod Locale module for Klipper
# Loads localized messages from zmod_locale.yml and provides access via printer['zlocale'](...)
# Requires zmod_locale.yml to be present in the Klipper config directory.
# zmod_locale.yml structure:
#
# messages:
#   MSG_HELLO: "Hello from ZMOD!"
#   MSG_TEST: "Hello from ZMOD! This is a test message. {value}"
# Usage:
#  simple call from macros
#   RESPOND TYPE=echo MSG="{ zlocale('MSG_HELLO') }"
#   RESPOND TYPE=echo MSG="{ zlocale('MSG_TEST', value='9999') }"

import logging
import yaml
import os

# IMPORTANT: The file must exist.
MESSAGES_FILENAME = 'zmod_locale.yml'

def _setup_logger():
    return logging.getLogger('klipper.zmod_locale')

def _detect_config_dir(printer):
    # 1) explicit override via env variable
    env_dir = os.getenv("ZMOD_CONFIG_DIR")
    if env_dir and os.path.isdir(env_dir):
        return env_dir

    # 2) find out from the Klipper 'configfile' object
    try:
        cfg = printer.lookup_object('configfile', None)
        if cfg:
            # try methods that return the path to the main file
            for meth in ('get_filename', 'get_main_config', 'get_config_file', 'get_base_path'):
                fn = getattr(cfg, meth, None)
                if callable(fn):
                    try:
                        path = fn()
                        if isinstance(path, str) and path:
                            if os.path.isfile(path):
                                return os.path.dirname(path)
                            if os.path.isdir(path):
                                return path
                    except Exception:
                        pass
            # try directly known attributes
            for attr in ('filename', 'main_config_path', 'config_path', 'config_dir', 'basedir', 'base_path'):
                path = getattr(cfg, attr, None)
                if isinstance(path, str) and path:
                    if os.path.isfile(path):
                        return os.path.dirname(path)
                    if os.path.isdir(path):
                        return path
    except Exception:
        pass

    # 3) rozumný výchozí stav pro tento image
    return os.path.join(os.path.expanduser("~"), "printer_data", "config")

class Localization:
    def __init__(self, config):
        #read debug option from [zmod_locale] section (defaults to False)
        try:
            self.debug = config.getboolean('debug', False)
        except Exception:
            self.debug = False

        self.printer = config.get_printer()
        self.logger = _setup_logger()

        # honor debug flag by enabling/disabling all logger output
        if not self.debug:
            self.logger.disabled = True
        else:
            self.logger.setLevel(logging.INFO)
        
        self.messages = {}
        
        # The path is detected automatically (env -> configfile -> fallback)
        self.config_dir = _detect_config_dir(self.printer)
        self.messages_file = os.path.join(self.config_dir, MESSAGES_FILENAME)

        self.logger.info("Config path: %s", self.messages_file)
        self.logger.info("ZLocale module ready. Attempting to load messages from: %s", self.messages_file)

        # Register the object immediately during initialization
        self.printer.add_object('zlocale', self)
        self.printer.register_event_handler("klippy:ready", self._handle_ready)

    def _inject_into_jinja(self):
        injected = False
        try:
            gcm = self.printer.lookup_object('gcode_macro', None)
            if gcm:
                # Try common attribute names seen across Klipper versions/forks
                for attr in ('j2_env', 'template_env', 'jinja2_env', 'env'):
                    env = getattr(gcm, attr, None)
                    if env:
                        env.globals['zlocale'] = self
                        self.logger.info("ZLocale injected into gcode_macro.%s", attr)
                        injected = True
                        break
                # Try registration methods if present
                for reg in ('register_template_global', 'add_template_global'):
                    fn = getattr(gcm, reg, None)
                    if fn:
                        fn('zlocale', self)
                        self.logger.info("ZLocale registered via gcode_macro.%s", reg)
                        injected = True
        except Exception as e:
            self.logger.error("Inject into gcode_macro failed: %s", e)

        # Fallback: inject into configfile Jinja (useful for some setups)
        try:
            cfg = self.printer.lookup_object('configfile', None)
            get_env = getattr(cfg, 'get_jinja2_environment', None)
            if get_env:
                env = get_env()
                env.globals['zlocale'] = self
                self.logger.info("ZLocale injected into configfile Jinja2")
                injected = True
        except Exception as e:
            self.logger.error("Inject into configfile Jinja2 failed: %s", e)

        if not injected:
            self.logger.warning("No Jinja2 environment found; use printer['zlocale'](...) in macros.")
    
    def _handle_ready(self):
        self._load_messages()
        self._inject_into_jinja()

    def _load_messages(self):
        """Loads messages from  file zmod_locale.yml."""
        if not os.path.exists(self.messages_file):            
            self.logger.error("!!! FATAL ERROR !!! Module will not function without zlocale.yml.")
            return

        try:
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                self.messages = {}
            elif isinstance(data, dict):
                if 'messages' in data:
                    if isinstance(data['messages'], dict):
                        self.messages = data['messages']
                    else:
                        self.logger.error("'messages' must be a dictionary (dict), but it is %s", type(data['messages']).__name__)
                        self.messages = {}
                else:
                    # flat format key: value
                    self.messages = data
            else:
                self.logger.error("The root of YAML must be a map (dict), but it is %s", type(data).__name__)
                self.messages = {}

            self.logger.info("ZLocale messages loaded successfully. Total keys: %d", len(self.messages))
        except Exception as e:
            self.logger.error("Error loading ZLocale messages from %s: %s", self.messages_file, e)
            self.messages = {}
    def get_msg(self, key, **kwargs):
        """Vrátí naformátovaný text pro daný klíč."""
        template = self.messages.get(key)
        
        if template is None:
            return f"ZLOCALE ERROR: Key '{key}' not found."

        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"ZLOCALE ERROR: Missing variable {e} for key '{key}'."
        except Exception as e:
            return f"ZLOCALE ERROR: Formatting failed for key '{key}': {e}"

    def __call__(self, key, **kwargs):
        """Allows calling directly from locale('KLIC', var=...)."""
        return self.get_msg(key, **kwargs)

def load_config(config):
    return Localization(config)