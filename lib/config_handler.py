import json
import logging
import os
import time
import traceback
from cryptography.fernet import Fernet, InvalidToken

module_logger = logging.getLogger('icad_alerting_api.config')

default_config = {
    "log_level": 1,
    "general": {
        "region": "US",
        "base_url": "http://localhost",
        "cookie_domain": "localhost",
        "cookie_secure": False,
        "cookie_name": "icad_alerting",
        "cookie_path": "/"
    },
    "audio_upload": {
        "allowed_mimetypes": ["audio/x-wav", "audio/x-m4a", "audio/mpeg"],
        "max_audio_length": 300,
        "max_file_size": 3
    }
}


def get_max_content_length(config_data, default_size_mb=3):
    try:
        # Attempt to retrieve and convert the max file size to an integer
        max_file_size = int(config_data.get("audio_upload", {}).get("max_file_size", default_size_mb))
    except (ValueError, TypeError) as e:
        # Log the error and exit if the value is not an integer or not convertible to one
        module_logger.error(f'Max File Size Must be an Integer: {e}')
        time.sleep(5)
        exit(1)
    else:
        # Return the size in bytes
        return max_file_size * 1024 * 1024


def deep_update(source, overrides):
    for key, value in overrides.items():
        if isinstance(value, dict):
            # Get the existing nested dictionary or create a new one
            node = source.setdefault(key, {})
            deep_update(node, value)
        else:
            source[key] = value


def generate_default_config():
    try:

        global default_config
        default_data = default_config.copy()
        default_data["general"]["base_url"] = os.getenv('BASE_URL', "http://localhost")
        default_data["general"]["cookie_domain"] = os.getenv('COOKIE_DOMAIN', "localhost")
        default_data["general"]["cookie_secure"] = bool(os.getenv('COOKIE_SECURE', False))
        default_data["general"]["cookie_name"] = os.getenv('COOKIE_NAME', "icad_alerting")
        default_data["general"]["cookie_path"] = os.getenv('COOKIE_PATH', "/")
        default_data['mysql'] = {}
        default_data["mysql"]["host"] = os.getenv('MYSQL_HOST', "mysql")
        default_data["mysql"]["port"] = int(os.getenv('MYSQL_PORT', 3306))
        default_data["mysql"]["user"] = os.getenv('MYSQL_USER', "icad_alerting")
        default_data["mysql"]["password"] = os.getenv('MYSQL_PASSWORD', "")
        default_data["mysql"]["database"] = os.getenv('MYSQL_DATABASE', "icad_alerting")
        default_data["redis"] = {}
        default_data["redis"]["host"] = os.getenv('REDIS_HOST', "redis")
        default_data["redis"]["port"] = int(os.getenv('REDIS_PORT', 6379))
        default_data["redis"]["password"] = os.getenv('REDIS_PASSWORD', "")

        return default_data

    except Exception as e:
        traceback.print_exc()
        module_logger.error(f'Error generating default configuration: {e}')
        return None


def encrypt_password(password, config_data):
    f = Fernet(config_data.get("fernet_key"))
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password


def is_fernet_token(possible_token, config_data):
    f = Fernet(config_data.get("fernet_key"))
    try:
        # Attempt to decrypt. If this works, it's likely a Fernet token.
        f.decrypt(possible_token.encode())
        return True
    except InvalidToken:
        # If decryption fails, it's not a valid Fernet token.
        return False


# Decrypt a password
def decrypt_password(encrypted_password, config_data):
    f = Fernet(config_data.get("fernet_key"))
    decrypted_password = f.decrypt(encrypted_password).decode()
    return decrypted_password


def generate_key_and_save_to_file(key_path):
    """
    Generates a new Fernet key and saves it to a file.
    """
    key = Fernet.generate_key()
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    module_logger.info(f"Encryption Key generated and saved to {key_path}")


def load_key_from_file(key_path):
    """
    Loads the Fernet key from a file or generates a new one if the file doesn't exist.
    """
    try:
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        module_logger.info(f"Encryption Key file {key_path} not found. Generating a new one.")
        generate_key_and_save_to_file(key_path)
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
    return key


def load_config_file(file_path):
    """
    Loads the configuration file and encryption key.
    """
    key_path = file_path.replace("config.json", "secret.key")

    # Load or generate the encryption key
    encryption_key = load_key_from_file(key_path)

    # Attempt to load the configuration file
    try:
        with open(file_path, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        module_logger.warning(f'Configuration file {file_path} not found. Creating default.')
        config_data = generate_default_config()  # Assuming this function is defined elsewhere
        if config_data:
            save_config_file(file_path, config_data)  # Assuming this function is defined elsewhere
    except json.JSONDecodeError:
        module_logger.error(f'Configuration file {file_path} is not in valid JSON format.')
        return None
    except Exception as e:
        module_logger.error(f'Unexpected Exception Loading file {file_path} - {e}')
        return None

    # Add the encryption key to the configuration data
    if not config_data:
        config_data = {}
    config_data["fernet_key"] = encryption_key

    return config_data


def save_config_file(file_path, default_data):
    """Creates a configuration file with default data if it doesn't exist."""
    try:
        with open(file_path, "w") as outfile:
            outfile.write(json.dumps(default_data, indent=4))
        return True
    except Exception as e:
        module_logger.error(f'Unexpected Exception Saving file {file_path} - {e}')
        return None

# def load_systems_agencies_detectors(db, system_id=None):
#     systems_config = {}
#     systems_result = get_systems(db, system_id)
#     if systems_result.get("success") and systems_result.get("result"):
#         for system in systems_result.get("result"):
#             agency_result = get_agencies(db, [system.get("system_id")])
#             if not agency_result.get("success") or not agency_result.get("result"):
#                 agency_result = {"result": []}
#             systems_config[system.get("system_id")] = system
#             systems_config["agencies"] = agency_result.get("result", [])
#
#     return systems_config
