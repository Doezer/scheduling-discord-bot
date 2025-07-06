import json
import threading
import logging
from typing import Any

CONFIG_FILE = 'config.json'
_config_lock = threading.Lock()

def load_config(file_path: str = CONFIG_FILE) -> dict:
    with _config_lock:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"Config file {file_path} not found. Returning empty config.")
            return {}

def save_config(config: dict, file_path: str = CONFIG_FILE):
    with _config_lock:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

def get_config_value(key: str, default: Any = None, file_path: str = CONFIG_FILE) -> Any:
    config = load_config(file_path)
    return config.get(key, default)

def set_config_value(key: str, value: Any, file_path: str = CONFIG_FILE):
    config = load_config(file_path)
    config[key] = value
    save_config(config, file_path)
