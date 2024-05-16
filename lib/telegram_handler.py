import os.path
from datetime import datetime, timezone
import logging

import requests

from lib.audio_file_handler import convert_wav_opus, download_wav_to_temp
from lib.config_handler import decrypt_password

module_logger = logging.getLogger('icad_alerting_api.telegram')


class TelegramAPI:

    def __init__(self, global_config_data, system_config_data, trigger_config_data=None):
        self.base_url = 'https://api.telegram.org/bot'
        self.global_config_data = global_config_data
        self.system_config_data = system_config_data
        self.trigger_config_data = trigger_config_data
        self.test_mode = self.global_config_data.get("general", {}).get("test_mode", True)

        self.bot_token = decrypt_password(self.system_config_data.get("telegram_bot_token", ""),
                                          self.global_config_data)
        self.channel = self.system_config_data.get("telegram_channel_id", "")

    def _send_request(self, method, payload, files=None):
        url = f'{self.base_url}{self.bot_token}/{method}'
        try:
            resp = requests.post(url, data=payload, files=files)
            resp.raise_for_status()
            module_logger.info("Successfully posted to telegram")
            return True
        except requests.exceptions.HTTPError as err:
            module_logger.error(f"Telegram Post Failed: {err.response.status_code} {err.response.text}")
            return False
        except requests.exceptions.RequestException as e:
            module_logger.error(f"Request failed: {e}")
            return False

    def post_text(self, alert_data, call_data):
        if not self.bot_token or not self.channel:
            module_logger.error(f"<<Telegram>> <<Post>> Bot token and channel ID must be provided,")

        trigger_list = []
        for trigger in alert_data:
            if trigger.get("telegram_enabled"):
                trigger_list.append(trigger.get("trigger_name"))

        post_body = self.generate_post_body(alert_data, call_data)
        if not post_body:
            return False

        payload = {
            'chat_id': self.channel,
            'text': post_body,
            'parse_mode': 'HTML'
        }
        result = self._send_request('sendMessage', payload)
        if result:
            module_logger.info(f"<<Telegram>> <<Text>> <<Post>> Successful.")

        return result

    def post_audio(self, alert_data, call_data):
        if not self.bot_token or not self.channel:
            module_logger.error(f"<<Telegram>> <<Audio>> <<Post>> Bot token and channel ID must be provided,")

        audio_wav_url = call_data.get("audio_wav_url", "")
        if not audio_wav_url:
            module_logger.error(f"<<Telegram>> <<Audio>> <<Post>> Audio file not in call data.")
            return False

        trigger_list = []
        for trigger in alert_data:
            if trigger.get("telegram_enabled"):
                trigger_list.append(trigger.get("trigger_name"))

        if len(trigger_list) < 1:
            module_logger.warning("Not Posting to <<Telegram>> no triggers enabled for Telegram.")
            return False

        opus_file = self._convert_to_opus(audio_wav_url)
        if not opus_file:
            module_logger.error("<<Telegram>> <<Audio>> <<Post>> failed: no OGG file converted.")
            return False

        try:

            post_body = self.generate_post_body(alert_data, call_data)
            if not post_body:
                return False

            with open(opus_file, 'rb') as audio_file:
                payload = {
                    'chat_id': self.channel,
                    "caption": post_body
                }
                files = {'voice': audio_file.read()}
                result = self._send_request('sendVoice', payload, files)
                if result:
                    module_logger.info(f"<<Telegram>> <<Audio>> <<Post>> Successful.")

                return result
        except IOError as e:
            module_logger.error(f"<<Telegram>> <<Audio>> <<Post>> Failed to open or read the OGG file: {e}")
            return False
        finally:
            if os.path.exists(opus_file):
                os.remove(opus_file)

    def generate_post_body(self, alert_data, call_data):
        try:
            post_body = "{timestamp}\n{trigger_list}\n{transcript}\niCAD Dispatch"
            if self.test_mode:
                post_body = f"TEST TEST TEST TEST TEST TEST\n\n{post_body}"

            # Convert the epoch timestamp to a datetime object
            current_time_dt = datetime.fromtimestamp(call_data.get("start_time", 0), tz=timezone.utc).astimezone()

            # Format the datetime object to a human-readable string with the timezone
            formatted_current_time = current_time_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

            trigger_list = "\n".join(
                [alert.get("trigger_name") for alert in alert_data if alert.get("telegram_enabled", False)])

            # Create a mapping
            mapping = {
                "trigger_list": trigger_list,
                "timestamp": formatted_current_time,
                "timestamp_epoch": call_data.get("start_time"),
                "transcript": call_data.get("transcript", {}).get("transcript", "No Transcript"),
                "audio_wav_url": call_data.get("audio_wav_url", ""),
                "audio_m4a_url": call_data.get("audio_m4a_url", ""),
                "stream_url": self.system_config_data.get("stream_url", "")
            }

            post_body = post_body.format_map(mapping)
            return post_body
        except Exception as e:
            module_logger.error(f"<<Telegram>> <<Post>> failed Unable to create telegram post body. {e}")
            return None

    def _convert_to_opus(self, audio_wav_url):
        try:
            wav_temp_file = download_wav_to_temp(audio_wav_url)
            if not wav_temp_file:
                return None

            opus_result = convert_wav_opus(wav_temp_file)
            os.remove(wav_temp_file)
            if opus_result:
                return opus_result
            else:
                module_logger.error("<<Telegram>> <<Audio>> <<Post>> Conversion to OPUS failed.")
                return None
        except Exception as e:
            module_logger.error(f"<<Telegram>> <<Audio>> <<Post>> Unexpected error during conversion: {e}")
            return None
