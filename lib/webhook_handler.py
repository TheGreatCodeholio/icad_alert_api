import json
import logging
import traceback
from datetime import datetime, timezone

import requests
from requests import HTTPError, Timeout, RequestException

from lib.helper_handler import generate_mapped_json

module_logger = logging.getLogger("icad_alerting_api.webhook_handler")


def update_system_webhooks(db, system_id, webhooks_data):
    try:
        # Fetch the current webhooks from the database
        current_webhooks = {}
        get_result = db.execute_query(
            "SELECT webhook_id, webhook_url, webhook_headers, webhook_body, enabled FROM radio_system_webhooks WHERE system_id = %s",
            (system_id,))
        if get_result.get("success") and get_result.get("result"):
            for webhook_data in get_result.get("result"):
                current_webhooks[webhook_data.get("webhook_id")] = webhook_data

        # Process each provided webhook update or addition
        for webhook in webhooks_data:
            webhook_id = webhook.get("webhook_id")
            webhook_url = webhook.get("webhook_url")
            webhook_headers = json.dumps(webhook.get("webhook_headers", {}))  # Convert dictionary to JSON string
            webhook_body = json.dumps(webhook.get("webhook_body", {}))
            enabled = 1 if webhook.get("enabled") else 0

            if webhook_id and webhook_id in current_webhooks:
                # Update existing webhook if there are changes
                if (current_webhooks[webhook_id]['webhook_url'] != webhook_url or
                        current_webhooks[webhook_id]['webhook_headers'] != webhook_headers or current_webhooks[webhook_id]['webhook_body'] != webhook_body or
                        current_webhooks[webhook_id]['enabled'] != enabled):
                    db.execute_commit(
                        "UPDATE radio_system_webhooks SET webhook_url = %s, webhook_headers = %s, webhook_body = %s, enabled = %s WHERE webhook_id = %s AND system_id = %s",
                        (webhook_url, webhook_headers, webhook_body, enabled, webhook_id, system_id))
            else:
                # Insert new webhook if it doesn't exist
                db.execute_commit(
                    "INSERT INTO radio_system_webhooks (system_id, webhook_url, webhook_headers, webhook_body, enabled) VALUES (%s, %s, %s, %s, %s)",
                    (system_id, webhook_url, webhook_headers, webhook_body, enabled))

        # Check for webhooks to remove
        existing_ids = set(current_webhooks.keys())
        provided_ids = {webhook.get("webhook_id") for webhook in webhooks_data if webhook.get("webhook_id")}
        ids_to_remove = existing_ids - provided_ids

        for webhook_id in ids_to_remove:
            db.execute_commit("DELETE FROM radio_system_webhooks WHERE system_id = %s AND webhook_id = %s",
                              (system_id, webhook_id))

        result = {"success": True, "message": "Webhooks updated successfully."}
    except Exception as e:
        result = {"success": False, "message": f"Failed to update webhooks: {e}"}

    return result


def update_trigger_webhooks(db, trigger_id, webhooks_data):
    try:
        # Fetch the current webhooks from the database
        current_webhooks = {}
        get_result = db.execute_query(
            "SELECT webhook_id, webhook_url, webhook_headers, webhook_body, enabled FROM alert_trigger_webhooks WHERE trigger_id = %s",
            (trigger_id,))
        if get_result.get("success") and get_result.get("result"):
            for webhook_data in get_result.get("result"):
                current_webhooks[webhook_data.get("webhook_id")] = webhook_data

        # Process each provided webhook update or addition
        for webhook in webhooks_data:
            webhook_id = webhook.get("webhook_id")
            webhook_url = webhook.get("webhook_url")
            webhook_headers = json.dumps(webhook.get("webhook_headers", {}))
            webhook_body = json.dumps(webhook.get("webhook_body", {}))   # Convert dictionary to JSON string
            enabled = 1 if webhook.get("enabled") else 0

            if webhook_id and webhook_id in current_webhooks:
                # Update existing webhook if there are changes
                if (current_webhooks[webhook_id]['webhook_url'] != webhook_url or
                        current_webhooks[webhook_id]['webhook_headers'] != webhook_headers or
                        current_webhooks[webhook_id]['webhook_body'] != webhook_body or
                        current_webhooks[webhook_id]['enabled'] != enabled):
                    db.execute_commit(
                        "UPDATE alert_trigger_webhooks SET webhook_url = %s, webhook_headers = %s, webhook_body = %s, enabled = %s WHERE webhook_id = %s AND trigger_id = %s",
                        (webhook_url, webhook_headers, webhook_body, enabled, webhook_id, trigger_id))
            else:
                # Insert new webhook if it doesn't exist
                db.execute_commit(
                    "INSERT INTO alert_trigger_webhooks (trigger_id, webhook_url, webhook_headers, webhook_body, enabled) VALUES (%s, %s, %s, %s, %s)",
                    (trigger_id, webhook_url, webhook_headers, webhook_body, enabled))

        # Check for webhooks to remove
        existing_ids = set(current_webhooks.keys())
        provided_ids = {webhook.get("webhook_id") for webhook in webhooks_data if webhook.get("webhook_id")}
        ids_to_remove = existing_ids - provided_ids

        for webhook_id in ids_to_remove:
            db.execute_commit("DELETE FROM alert_trigger_webhooks WHERE trigger_id = %s AND webhook_id = %s",
                              (trigger_id, webhook_id))

        result = {"success": True, "message": "Webhooks updated successfully."}
    except Exception as e:
        result = {"success": False, "message": f"Failed to update webhooks: {e}"}

    return result


class WebHook:
    def __init__(self, global_config_data, system_config_data, trigger_config_data=None):
        self.global_config_data = global_config_data
        self.system_config_data = system_config_data
        self.trigger_config_data = trigger_config_data

    def _send_request(self, url, webhook_headers, webhook_body):
        try:
            if webhook_headers is None:
                webhook_headers = {'Content-Type': 'application/json'}
            elif 'Content-Type' not in webhook_headers:
                webhook_headers['Content-Type'] = 'application/json'

            if webhook_body is None:
                module_logger.error(F'No Webhook Body Can not post webhook.')
                return

            response = requests.post(url,
                                     json=webhook_body,
                                     headers=webhook_headers,
                                     timeout=10
                                     )

            response.raise_for_status()  # Raise an exception for HTTP errors

            module_logger.debug(f"<<Webhook>> Successful: URL {url}")
            return True
        except HTTPError as e:
            module_logger.error(
                f"<<Webhook>> <<Failed>> HTTP error occurred for URL {url}: {e.response.status_code} {e.response.text}")
            return False
        except ConnectionError as e:
            module_logger.error(f"<<Webhook>> <<Failed>> Connection error occurred for URL {url}: {e}")
            return False
        except Timeout as e:
            module_logger.error(f"<<Webhook>> <<Failed>> Timeout error occurred for URL {url}: {e}")
            return False
        except RequestException as e:
            module_logger.error(f"<<Webhook>> <<Failed>> Request error occurred for URL {url}: {e}")
            return False
        except Exception as e:
            traceback.print_exc()
            module_logger.error(f"<<Webhook>> <<Failed>> Unexpected error occurred for URL {url}: {e}")
            return False

    def send_webhook(self, webhook_url, wehbook_headers, webhook_body, alert_data, call_data):

        test_mode = self.global_config_data.get("general", {}).get("test_mode", True)

        if self.system_config_data and not self.trigger_config_data:
            stream_url = self.system_config_data.get("stream_url") or ""
        elif self.system_config_data and self.trigger_config_data:

            stream_url = self.trigger_config_data.get("stream_url") or ""
            if not stream_url:
                stream_url = self.system_config_data.get("stream_url") or ""
        else:
            stream_url = self.global_config_data.get("stream_url") or ""

        try:

            webhook_json = generate_mapped_json(webhook_body, alert_data, call_data, stream_url, test_mode)

            # Log the webhook JSON to debug issues with the payload
            module_logger.debug(f"Webhook JSON: {webhook_json}")

            post_result = self._send_request(webhook_url, wehbook_headers, webhook_json)
            return post_result
        except Exception as e:
            traceback.print_exc()
            module_logger.error(f"<<Webhook>> Post Failure:\n {repr(e)}")
            return False
