import logging

from lib.email_handler import EmailSender, generate_trigger_alert_email, generate_system_alert_email
from lib.facebook_handler import FacebookAPI
from lib.pushover_handler import PushoverSender
from lib.telegram_handler import TelegramAPI
from lib.webhook_handler import WebHook

module_logger = logging.getLogger('icad_alerting_api.alert_actions')


def run_trigger_actions(global_config_data, system_config_data, trigger_config, alert_data, call_data):
    module_logger.info(f"Running Trigger Actions for {trigger_config.get('trigger_name')}")

    module_logger.debug(f"Call Data: {call_data}")
    module_logger.debug(f"Alert Data: {alert_data}")

    # Send Alert Emails
    if system_config_data.get("email_enabled", False):
        em = EmailSender(global_config_data, system_config_data)

        subject, body = generate_trigger_alert_email(global_config_data, system_config_data, trigger_config, alert_data,
                                                     call_data)

        if not subject or not body:
            module_logger.warning(
                f"Skipping Sending Email for Trigger {trigger_config.get('trigger_name')} Unable to get email body or subject.")
        else:
            email_list = []
            for email in trigger_config.get("trigger_emails", []):
                if email.get("enabled"):
                    email_list.append(email.get("email_address"))

            if len(email_list) >= 1:
                email_result = em.send_email(email_list, subject, body)
                if email_result:
                    module_logger.info("<<Trigger>> <<Email>> Sent Successfully")
            else:
                module_logger.warning(
                    f"Skipping Sending Email for Trigger {system_config_data.get('system_name')} No alert emails set")

    # Send Trigger Alert Pushover
    if system_config_data.get("pushover_enabled", False):
        PushoverSender(global_config_data, system_config_data, trigger_config).send_text_alert_push(alert_data,
                                                                                                    call_data)

    # Send to Trigger Webhooks
    for webhook in trigger_config.get("trigger_webhooks", []):
        if webhook.get("enabled"):
            WebHook(global_config_data, system_config_data, trigger_config).send_webhook(webhook.get("webhook_url"),
                                                                                         webhook.get("webhook_headers",
                                                                                                     {}),
                                                                                         webhook.get("webhook_body",
                                                                                                     {}), alert_data,
                                                                                         call_data)


def run_global_actions(global_config_data, system_config_data, alert_data, call_data):
    module_logger.info(f"Running System Actions for {system_config_data.get('system_name')}")

    module_logger.debug(f"Call Data: {call_data}")
    module_logger.debug(f"Alert Data: {alert_data}")

    # Send Alert Emails
    if system_config_data.get("email_enabled", False):
        em = EmailSender(global_config_data, system_config_data)

        subject, body = generate_system_alert_email(global_config_data, system_config_data, alert_data, call_data)

        if not subject or not body:
            module_logger.warning(
                f"Skipping Sending Email for System {system_config_data.get('system_name')} Unable to get email body or subject.")
        else:
            email_list = []
            for email in system_config_data.get("system_emails", []):
                if email.get("enabled"):
                    email_list.append(email.get("email_address"))

            if len(email_list) >= 1:
                email_result = em.send_email(email_list, subject, body)
                if email_result:
                    module_logger.info("<<System>> <<Email>> Sent Successfully")
            else:
                module_logger.warning(
                    f"Skipping Sending <<Email>> for <<System>> {system_config_data.get('system_name')} No alert emails set")

    # Send Global Alert Pushover
    if system_config_data.get("pushover_enabled", False):
        PushoverSender(global_config_data, system_config_data).send_text_alert_push(alert_data, call_data)

    # Send Alert Facebook
    if system_config_data.get("facebook_enabled", False):
        FacebookAPI(global_config_data, system_config_data).post_message(alert_data, call_data)

    # Send Alert Telegram
    if system_config_data.get("telegram_enabled", False):
        TelegramAPI(global_config_data, system_config_data).post_audio(alert_data, call_data)

    # Send to System Webhooks
    for webhook in system_config_data.get("system_webhooks", []):
        if webhook.get("enabled"):
            WebHook(global_config_data, system_config_data).send_webhook(webhook.get("webhook_url"),
                                                                         webhook.get("webhook_headers", {}),
                                                                         webhook.get("webhook_body", {}), alert_data,
                                                                         call_data)
