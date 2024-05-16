import logging
import tempfile

import requests

from lib.shell_handler import run_command

module_logger = logging.getLogger('icad_alerting_api.alert_actions')


def download_wav_to_temp(url):
    """
    Downloads a WAV file from the given URL to a temporary file path in memory.

    Parameters:
    - url (str): The URL of the WAV file.

    Returns:
    - str: The path to the temporary WAV file.

    Raises:
    - ValueError: If the URL does not point to a WAV file.
    - requests.exceptions.RequestException: For network-related errors.
    """
    try:
        # Check if the URL points to a WAV file
        if not url.lower().endswith('.wav'):
            raise ValueError("The URL does not point to a WAV file.")

        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        module_logger.info("WAV File Downloaded Successfully")
        return temp_file_path

    except requests.exceptions.RequestException as e:
        module_logger.error(f"Network error: {e}")
        raise
    except ValueError as e:
        module_logger.error(f"Value error: {e}")
        raise
    except Exception as e:
        module_logger.error(f"An unexpected error occurred: {e}")
        raise


def convert_wav_opus(wav_file_path):
    ogg_file = wav_file_path.replace(".wav", ".ogg")
    command = ['ffmpeg', '-y', '-i', wav_file_path, '-ac', '1', '-map', '0:a', '-strict', '-2', '-codec:a',
               'opus', '-b:a', '128k', ogg_file]

    ogg_convert_result = run_command(command, timeout=600)
    if ogg_convert_result:
        return ogg_file
    else:
        return None