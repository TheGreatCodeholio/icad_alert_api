import os
from datetime import datetime, timezone
import logging

import requests

from lib.config_handler import decrypt_password
from lib.helper_handler import generate_mapped_content

module_logger = logging.getLogger('icad_alerting_api.facebook')


class FacebookAPI:
    def __init__(self, global_config_data, system_config_data, trigger_config_data=None):
        """
            Initializes the FacebookAPI class with the necessary tokens and IDs.

            :param dict facebook_config: A dictionary containing the necessary Facebook credentials.
        """
        self.global_config_data = global_config_data
        self.system_config_data = system_config_data
        self.trigger_config_data = trigger_config_data
        self.test_mode = self.global_config_data.get("general", {}).get("test_mode", True)

    def _make_request(self, method, url, payload):
        try:
            response = requests.request(method, url, data=payload)
            response.raise_for_status()
            return {'success': True, 'message': 'Success', 'result': response.json()}
        except requests.RequestException as e:
            module_logger.error(f"Error in {method} request: {e}")
            return {'success': False, 'message': str(e), 'result': None}

    def post_to_page(self, page_id, page_token, message):
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"

        payload = {"message": message, "access_token": page_token}
        return self._make_request("POST", url, payload)

    def comment_on_page_post(self, post_id, page_token, message):
        url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
        payload = {"message": message, "access_token": page_token}
        return self._make_request("POST", url, payload)

    def post_message(self, alert_data, call_data):
        trigger_list = []
        for trigger in alert_data:
            if trigger.get("facebook_enabled"):
                trigger_list.append(trigger.get("trigger_name"))

        if len(trigger_list) < 1:
            module_logger.warning("Not Posting to <<Facebook>> Page no triggers enabled for Facebook.")
            return False

        module_logger.info("Posting to <<Facebook>> Page")

        page_id = self.system_config_data.get("facebook_page_id", "")
        comment_enabled = self.system_config_data.get("facebook_comment_enabled", "")

        if not page_id:
            module_logger.warning(f"<<Facebook>> <<Post>> <<Failed>> no page id given.")
            return False

        try:
            facebook_page_token = decrypt_password(self.system_config_data.get("facebook_page_token"),
                                                   self.global_config_data)

            facebook_message = self.generate_facebook_message(alert_data, call_data)
            facebook_comment = self.generate_facebook_comment(alert_data, call_data)

            page_response = self.post_to_page(page_id, facebook_page_token, facebook_message)
            if page_response.get('success', False):
                module_logger.info("<<Facebook>> <<Post>> page successful.")
                if comment_enabled:
                    page_post_id = page_response.get('result', {}).get('id', "")
                    if not page_post_id:
                        module_logger.error("<<Facebook>> <<Post>> unable to post comment, not post id returned.")
                        return page_response.get('success')

                    comment_response = self.comment_on_page_post(page_post_id, facebook_page_token, facebook_comment)

                    if comment_response.get("success"):
                        module_logger.info("<<Facebook>> <<Post>> page comment successful.")

                    return comment_response.get("success", False)
                else:
                    module_logger.warning("<<Facebook>> <<Post>> not posting post comment. Comment disabled.")
            else:
                return page_response.get("success", False)

        except Exception as e:
            module_logger.error(f"<<Facebook>> <<Post>> Unexpected error: {e}")
            return False

    def generate_facebook_message(self, alert_data, call_data):

        post_body_template = self.system_config_data.get("facebook_post_body",
                                                         "{timestamp} Departments:\n{trigger_list}\n\nDispatch Audio:\n{audio_wav_url}")

        post_body = generate_mapped_content(post_body_template, alert_data, call_data, self.system_config_data.get("stream_url") or "", self.test_mode)
        return post_body

    def generate_facebook_comment(self, alert_data, call_data):
        comment_body_template = self.system_config_data.get("facebook_comment_body", "{transcript}\n{stream_url}")

        comment_body = generate_mapped_content(comment_body_template, alert_data, call_data, self.system_config_data.get("stream_url") or "", self.test_mode)

        return comment_body
