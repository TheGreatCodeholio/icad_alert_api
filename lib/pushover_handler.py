import json
from datetime import datetime, timezone

import requests
from requests.exceptions import RequestException, HTTPError, Timeout
import logging


from lib.config_handler import decrypt_password
from lib.helper_handler import generate_mapped_content

module_logger = logging.getLogger('icad_alerting_api.pushover')


class PushoverSender:
    """PushoverSender is a class responsible for sending push notifications with given configurations.

    Attributes:
        config_data (dict): A dictionary containing configuration data.
        detector_data (dict): A dictionary containing detector data.
    """

    def __init__(self, global_config_data, system_config_data=None, trigger_config_data=None):
        """Initializes the PushoverSender with configuration and detector data.

        Args:
            config_data (dict): A dictionary containing configuration data.
            detector_data (dict): A dictionary containing detector data.

        Raises:
            ValueError: If config_data or detector_data are not dictionaries or are missing expected keys.
        """
        self.global_config_data = global_config_data
        self.system_config_data = system_config_data
        self.trigger_config_data = trigger_config_data

    def send_text_alert_push(self, alert_data, call_data):
        """Sends a push notification with the given parameters.

        Args:
            alert_data (dict): A dictionary containing data from triggered alert.
            call_data (dict): A dictionary containing metadata from processed call.

        Returns:
            True if successful or False if failed
        """

        test_mode = self.global_config_data.get("general", {}).get("test_mode", True)

        try:

            trigger_list = ", ".join([triggered_alert.get("trigger_name") for triggered_alert in alert_data])

            if self.system_config_data and not self.trigger_config_data:
                # This is a system pushover
                pushover_subject = self.system_config_data.get("pushover_subject")
                pushover_body = self.system_config_data.get("pushover_body")
                pushover_sound = self.system_config_data.get("sound")
                pushover_group_token = decrypt_password(self.system_config_data.get("pushover_group_token"),
                                                        self.global_config_data)
                pushover_app_token = decrypt_password(self.system_config_data.get("pushover_app_token"),
                                                      self.global_config_data)



                stream_url = self.system_config_data.get("stream_url") or ""

                group_name = "System"

            elif self.system_config_data and self.trigger_config_data:
                # this is a trigger pushover
                if not self.trigger_config_data.get("pushover_subject"):
                    pushover_subject = self.system_config_data.get("pushover_subject")
                else:
                    pushover_subject = self.trigger_config_data.get("pushover_subject")

                if not self.trigger_config_data.get("pushover_body"):
                    pushover_body = self.system_config_data.get("pushover_body")
                else:
                    pushover_body = self.trigger_config_data.get("pushover_body")

                if not self.trigger_config_data.get("sound"):
                    pushover_sound = self.system_config_data.get("sound")
                else:
                    pushover_sound = self.trigger_config_data.get("sound")


                pushover_group_token = decrypt_password(self.trigger_config_data.get("pushover_group_token"),
                                                        self.global_config_data)
                pushover_app_token = decrypt_password(self.trigger_config_data.get("pushover_app_token"),
                                                      self.global_config_data)

                if not pushover_subject or not pushover_body:
                    module_logger.error("<<Failed>> sending <<Pushover>> missing pushover subject or pushover body.")

                if not pushover_group_token or not pushover_app_token:
                    module_logger.error("<<Failed>> sending <<Pushover>> missing pushover app or group token.")

                stream_url = self.trigger_config_data.get("stream_url") or ""
                if not stream_url:
                    stream_url = self.system_config_data.get("stream_url") or ""

                group_name = trigger_list

            else:
                module_logger.error("<<Failed>> sending <<Pushover>> no system or trigger config data.")
                return False


            # Use the mapping to format the strings
            pushover_subject = generate_mapped_content(pushover_subject, alert_data, call_data, stream_url, test_mode)
            pushover_body = generate_mapped_content(pushover_body, alert_data, call_data, stream_url, test_mode)

            if pushover_app_token and pushover_group_token:
                request_result = self._send_request(pushover_app_token, pushover_group_token, pushover_subject,
                                                    pushover_body,
                                                    pushover_sound, group_name)
                return request_result
            else:
                module_logger.error(f"<<Pushover>> <<Failed>> Missing Pushover APP or Group Token for {group_name}")
                return False


        except Exception as e:
            module_logger.error(f"Pushover Send Failure:\n {repr(e)}")
            return False

    def _send_request(self, app_token, group_token, subject, body, sound, group_name="System", image_path=None):
        try:
            url = "https://api.pushover.net/1/messages.json"
            post_data = {
                "token": app_token,
                "user": group_token,
                "html": 1,
                "message": body,
                "title": subject,
                "sound": sound
            }

            files = {}
            if image_path:
                try:
                    with open(image_path, "rb") as push_image:
                        files["attachment"] = push_image
                except FileNotFoundError:
                    module_logger.error(f"<<Pushover>> <<Failed>> sending image File not found: {image_path}")
                    return False
                except IOError as e:
                    module_logger.error(
                        f"<<Pushover>> <<Failed>> sending image IO error occurred while opening the file {image_path}: {e}")
                    return False
                except Exception as e:
                    module_logger.error(
                        f"<<Pushover>> <<Failed>> Unexpected error occurred while opening the image file {image_path}: {e}")
                    return False

            response = requests.post(url,
                                     data=post_data,
                                     files=files,
                                     timeout=10
                                     )

            response.raise_for_status()  # Raise an exception for HTTP errors

            module_logger.info(f"<<Pushover>> Successful: Group {group_name}")
            return True
        except HTTPError as e:
            if e.response.status_code == 400:
                response_json = json.loads(e.response.text)
                for error in response_json.get("errors"):
                    if error == "group has no users or active devices in it":
                        module_logger.warning(f"<<Pushover>> No recipients in Group {group_name}")
                        return True

            module_logger.error(
                f"<<Pushover>> <<Failed>> HTTP error occurred for Group {group_name}: {e.response.status_code} {e.response.text}")
            return False
        except ConnectionError as e:
            module_logger.error(f"<<Pushover>> <<Failed>> Connection error occurred for Group {group_name}: {e}")
            return False
        except Timeout as e:
            module_logger.error(f"<<Pushover>> <<Failed>> Timeout error occurred for Group {group_name}: {e}")
            return False
        except RequestException as e:
            module_logger.error(f"<<Pushover>> <<Failed>> Request error occurred for Group {group_name}: {e}")
            return False
        except Exception as e:
            module_logger.error(f"<<Pushover>> <<Failed>> Unexpected error occurred for Group {group_name}: {e}")
            return False
