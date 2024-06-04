import json
import logging
import uuid

from lib.alert_trigger_handler import get_alert_triggers
from lib.config_handler import is_fernet_token, encrypt_password

module_logger = logging.getLogger("icad_alerting_api.system_handler")


def get_systems(db, system_id=None, system_short_name=None, with_triggers=True):
    # Base query without GROUP_CONCAT for emails
    base_query = """
SELECT 
    rs.system_id,
    rs.system_short_name,
    rs.system_name,
    rs.system_county,
    rs.system_state,
    rs.system_fips,
    rs.system_api_key,
    rs.stream_url,
    rses.email_enabled,
    rses.smtp_hostname,
    rses.smtp_password,
    rses.smtp_port,
    rses.smtp_username,
    rses.email_address_from,
    rses.email_text_from,
    rses.email_alert_subject,
    rses.email_alert_body,
    rsps.pushover_enabled,
    rsps.pushover_group_token,
    rsps.pushover_app_token,
    rsps.pushover_body,
    rsps.pushover_subject,
    rsps.pushover_sound,
    rsts.telegram_enabled,
    rsts.telegram_bot_token,
    rsts.telegram_channel_id,
    rsfs.facebook_enabled,
    rsfs.facebook_page_id,
    rsfs.facebook_page_token,
    rsfs.facebook_comment_enabled,
    rsfs.facebook_post_body,
    rsfs.facebook_comment_body,
    GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"webhook_id": "', rsws.webhook_id, 
            '", "enabled": "', rsws.enabled,
            '", "webhook_url": "', rsws.webhook_url,
            '", "webhook_headers": "', rsws.webhook_headers, '"}',
            '", "webhook_body": "', rsws.webhook_body, '"}',
        ) SEPARATOR '|') AS system_webhooks,
    GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"email_id": "', rse.email_id, 
            '", "email_address": "', rse.email_address,
            '", "enabled": "', rse.enabled, '"}'
        ) SEPARATOR '|') AS system_emails
FROM radio_systems rs
LEFT JOIN icad_alerting.radio_system_email_settings rses on rs.system_id = rses.system_id
LEFT JOIN icad_alerting.radio_system_pushover_settings rsps on rs.system_id = rsps.system_id
LEFT JOIN icad_alerting.radio_system_telegram_settings rsts on rs.system_id = rsts.system_id
LEFT JOIN icad_alerting.radio_system_emails rse on rs.system_id = rse.system_id
LEFT JOIN icad_alerting.radio_system_webhooks rsws on rs.system_id = rsws.system_id
LEFT JOIN icad_alerting.radio_system_facebook_settings rsfs on rs.system_id = rsfs.system_id
"""

    # Building the WHERE clause based on provided arguments
    where_clauses = []
    parameters = []
    if system_id:
        where_clauses.append("rs.system_id = %s")
        parameters.append(system_id)
    if system_short_name:
        where_clauses.append("rs.system_short_name = %s")
        parameters.append(system_short_name)

    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)
        final_query = f"{base_query} {where_clause} GROUP BY rs.system_id"
    else:
        final_query = f"{base_query} GROUP BY rs.system_id"

    systems_result = db.execute_query(final_query, tuple(parameters) if parameters else None)
    if not systems_result.get("success"):
        module_logger.error("Systems Result Empty")
        return systems_result

    for system in systems_result.get("result"):

        system["email_enabled"] = bool(int(system.get('email_enabled')))
        system["telegram_enabled"] = bool(int(system.get('telegram_enabled')))
        system["facebook_enabled"] = bool(int(system.get('facebook_enabled')))
        system["pushover_enabled"] = bool(int(system.get('pushover_enabled')))

        # Processing 'system_emails'
        if system['system_emails']:
            email_items = system['system_emails'].split('|')
            system['system_emails'] = [json.loads(email.strip()) for email in email_items if email.strip()]
            for email in system['system_emails']:
                module_logger.debug(email)
                email['enabled'] = bool(int(email['enabled']))  # Convert "1"/"0" to True/False
                email['email_id'] = int(email['email_id'])
        else:
            system['system_emails'] = []

        # Processing 'system_webhooks'
        if system['system_webhooks']:
            webhook_items = system['system_webhooks'].split('|')
            system['system_webhooks'] = [json.loads(webhook.strip()) for webhook in webhook_items if webhook.strip()]
            for webhook in system['system_webhooks']:
                webhook['enabled'] = bool(int(webhook['enabled']))
                webhook['webhook_id'] = int(webhook['webhook_id'])
                webhook['webhook_headers'] = json.loads(webhook['webhook_headers'])
                webhook['webhook_body'] = json.loads(webhook['webhook_body'])
        else:
            system['system_webhooks'] = []

        if with_triggers:
            trigger_result = get_alert_triggers(db, system_ids=[system.get('system_id')], trigger_id=None)
            if not trigger_result.get("success"):
                module_logger.warning("Trigger Result Empty")
                system["alert_triggers"] = []
            # Add the systems triggers to the system data.
            system["alert_triggers"] = trigger_result['result'] if trigger_result['result'] else []
        else:
            system["alert_triggers"] = []

    return systems_result


def check_for_system(db, system_name=None, system_id=None):
    if not system_id:
        query = f"SELECT * FROM radio_systems WHERE system_name = %s"
        params = (system_name,)
    else:
        query = f"SELECT * FROM radio_systems WHERE system_id = %s"
        params = (system_id,)

    result = db.execute_query(query, params, fetch_mode='one')
    return result.get("result", {})


def add_system(db, system_data):
    if not system_data:
        module_logger.warning(f"System Data Empty")
        return {"success": False, "message": "System Data Empty", "result": []}

    result = check_for_system(db, system_name=system_data.get('system_name'))
    if result:
        module_logger.warning(f"System already exists: {result}")
        return {"success": False, "message": f"System already exists: {result}", "result": []}

    api_key = str(uuid.uuid4())
    query = "INSERT INTO `radio_systems` (system_short_name, system_name, system_county, system_state, system_fips, system_api_key, stream_url) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    params = (
        system_data.get('system_short_name').strip().lower() or None, system_data.get('system_name') or None,
        system_data.get("system_county") or None, system_data.get("system_state") or None,
        system_data.get("system_fips") or None, api_key, system_data.get("stream_url") or None
    )

    result = db.execute_commit(query, params, return_row=True)

    if result['success'] and result['result']:
        system_id = result['result']  # Assuming this returns the new system's ID
        module_logger.info(f"New system added with ID: {system_id}")

        # Insert default settings for the new system
        insert_default_system_settings(db, system_id)
        module_logger.info("Default settings inserted for the new system.")
        result['message'] = f"New system added with ID: {system_id}"
    else:
        result['success'] = False
        system_id = None
        result['message'] = "Failed to add new system."
        module_logger.error("Failed to add new system.")

    return {"success": result['success'], "message": result.get("message"), "result": system_id}


def insert_default_system_settings(db, system_id):
    try:
        # Insert default email settings
        db.execute_commit(
            "INSERT INTO radio_system_email_settings (system_id, email_alert_body) VALUES (%s, %s)",
            (system_id,
             "{trigger_list} Alert at {timestamp}<br><br>{transcript}<br><br><a href=\"{audio_wav_url}\">Click for Dispatch Audio</a><br><br><a href=\"{stream_url}\">Click Audio Stream</a>")
        )

        # Insert default pushover settings
        db.execute_commit(
            "INSERT INTO radio_system_pushover_settings (system_id, pushover_body) VALUES (%s, %s)",
            (system_id,
             "<font color=\"red\"><b>{trigger_list}</b></font><br><br><a href=\"{audio_wav_url}\">Click for Dispatch Audio</a><br><br><a href=\"{stream_url}\">Click Audio Stream</a>")
        )

        # Insert default Facebook settings
        db.execute_commit(
            "INSERT INTO radio_system_facebook_settings (system_id) VALUES (%s)",
            (system_id,)
        )

        # Insert default telegram settings
        db.execute_commit(
            "INSERT INTO radio_system_telegram_settings (system_id) VALUES (%s)",
            (system_id,)
        )

        module_logger.info(f"Default settings inserted successfully for system_id: {system_id}")
    except Exception as e:
        module_logger.error(f"Failed to insert default settings for system_id: {system_id}. Error: {e}")


def update_system_general(db, system_data):
    if not system_data:
        module_logger.warning(f"System Data Empty")
        return {"success": False, "message": "System Data Empty", "result": []}

    result = check_for_system(db, system_id=system_data.get('system_id'))
    module_logger.warning(result)

    query = f"UPDATE `radio_systems` SET system_short_name = %s, system_name = %s, system_county = %s, system_state = %s, system_fips = %s, system_api_key = %s, stream_url = %s WHERE system_id = %s"
    params = (
        system_data.get('system_short_name').strip().lower() or None, system_data.get('system_name') or None,
        system_data.get("system_county") or None,
        system_data.get("system_state") or None,
        system_data.get("system_fips") or None, system_data.get('system_api_key') or None,
        system_data.get("stream_url") or None, system_data.get('system_id'))
    result = db.execute_commit(query, params)

    return result


def update_system_email_settings(db, system_data, config_data):
    smtp_password = system_data.get("smtp_password") or None

    try:
        if smtp_password is not None:
            if not is_fernet_token(smtp_password, config_data):
                smtp_password = encrypt_password(smtp_password, config_data)

        # Insert updated email settings
        result = db.execute_commit(
            "UPDATE radio_system_email_settings SET email_enabled = %s, smtp_hostname = %s, smtp_port = %s, smtp_username = %s, "
            "smtp_password = %s, email_address_from = %s, email_text_from = %s, "
            "email_alert_subject = %s, email_alert_body = %s WHERE system_id = %s",
            (
                system_data.get("email_enabled") or 0, system_data.get("smtp_hostname") or None,
                system_data.get("smtp_port") or None, system_data.get("smtp_username") or None,
                smtp_password,
                system_data.get("email_address_from") or "dispatch@example.com",
                system_data.get("email_text_from") or "iCAD Dispatch",
                system_data.get("email_alert_subject") or "Dispatch Alert",
                system_data.get("email_alert_body") or
                "{agency_list} Alert at {timestamp}<br><br>{transcript}<br><br><a href=\"{audio_wav_url}\">Click for Dispatch Audio</a><br><br><a href=\"{stream_url}\">Click Audio Stream</a>",
                system_data.get("system_id"))
        )
    except Exception as e:
        module_logger.error(f"Unexpected Exception when saving system email settings: {e}")
        result = {"success": False, "message": f"Unexpected Exception when saving system email settings: {e}",
                  "result": []}

    return result


def update_system_alert_emails(db, system_id, emails_data):
    try:
        # Fetch the current emails from the database
        current_emails = {}
        get_result = db.execute_query(
            "SELECT email_id, email_address, enabled FROM radio_system_emails WHERE system_id = %s",
            (system_id,))
        if get_result.get("success") and get_result.get("result"):
            for email_data in get_result.get("result"):
                current_emails[email_data.get("email_id")] = email_data

        # Process each provided email update or addition
        for email in emails_data:
            email_id = email.get("email_id")
            email_address = email.get("email_address")
            enabled = 1 if email.get("enabled") else 0

            if email_id and email_id in current_emails:
                # Update existing email if there are changes
                if current_emails[email_id]['email_address'] != email_address or current_emails[email_id][
                    'enabled'] != enabled:
                    db.execute_commit(
                        "UPDATE radio_system_emails SET email_address = %s, enabled = %s WHERE email_id = %s AND system_id = %s",
                        (email_address, enabled, email_id, system_id))
            else:
                # Insert new email if it doesn't exist
                db.execute_commit(
                    "INSERT INTO radio_system_emails (system_id, email_address, enabled) VALUES (%s, %s, %s)",
                    (system_id, email_address, enabled))

        # Check for emails to remove
        existing_ids = set(current_emails.keys())
        provided_ids = {email.get("email_id") for email in emails_data if email.get("email_id")}
        ids_to_remove = existing_ids - provided_ids

        for email_id in ids_to_remove:
            db.execute_commit("DELETE FROM radio_system_emails WHERE system_id = %s AND email_id = %s",
                              (system_id, email_id))

        result = {"success": True, "message": "Emails updated successfully."}
    except Exception as e:
        result = {"success": False, "message": f"Failed to update emails: {e}"}

    return result


def update_system_pushover_settings(db, system_data, config_data):
    pushover_group_token = system_data.get("pushover_group_token")
    pushover_app_token = system_data.get("pushover_app_token")

    try:

        if pushover_group_token is not None:
            if not is_fernet_token(pushover_group_token, config_data):
                pushover_group_token = encrypt_password(pushover_group_token, config_data)

        if pushover_app_token is not None:
            if not is_fernet_token(pushover_app_token, config_data):
                pushover_app_token = encrypt_password(pushover_app_token, config_data)

        # Update Pushover settings
        result = db.execute_commit(
            "UPDATE radio_system_pushover_settings SET pushover_enabled = %s, pushover_group_token = %s, pushover_app_token = %s, pushover_body = %s, pushover_subject = %s, pushover_sound = %s WHERE system_id = %s",
            (system_data.get("pushover_enabled", 0), pushover_group_token or None,
             pushover_app_token or None,
             system_data.get("pushover_body") or
             "<font color=\"red\"><b>{trigger_name}</b></font><br><br><a href=\"{audio_wav_url}\">Click for Dispatch Audio</a><br><br><a href=\"{stream_url}\">Click Audio Stream</a>",
             system_data.get("pushover_subject") or "Dispatch Alert", system_data.get("pushover_sound") or "pushover",
             system_data.get("system_id")
             )
        )

    except Exception as e:
        module_logger.error(f"Unexpected Exception when saving system pushover settings: {e}")
        result = {"success": False, "message": f"Unexpected Exception when saving system pushover settings: {e}",
                  "result": []}

    return result


def update_system_facebook_settings(db, system_data, config_data):
    facebook_page_token = system_data.get("facebook_page_token")
    if facebook_page_token:
        if not is_fernet_token(facebook_page_token, config_data):
            facebook_page_token = encrypt_password(facebook_page_token, config_data)

    try:
        # Update facebook settings
        result = db.execute_commit(
            "UPDATE radio_system_facebook_settings SET facebook_enabled = %s, facebook_page_id = %s, facebook_page_token = %s, facebook_comment_enabled = %s, facebook_post_body = %s, facebook_comment_body = %s WHERE system_id = %s",
            (system_data.get("facebook_enabled") or 0, system_data.get("facebook_page_id") or None,
             facebook_page_token or None, system_data.get("facebook_comment_enabled") or 0,
             system_data.get(
                 "facebook_post_body") or '{timestamp} Departments:\n{trigger_list}\n\nDispatch Audio:\n{mp3_url}',
             system_data.get("facebook_comment_body") or '{transcript}\n{stream_url}',
             system_data.get("system_id"))
        )
    except Exception as e:
        module_logger.error(f"Unexpected Exception when saving system telegram settings: {e}")
        result = {"success": False, "message": f"Unexpected Exception when saving system telegram settings: {e}",
                  "result": []}

    return result


def update_system_telegram_settings(db, system_data, config_data):
    telegram_bot_token = system_data.get("telegram_bot_token")
    if telegram_bot_token:
        if not is_fernet_token(telegram_bot_token, config_data):
            telegram_bot_token = encrypt_password(telegram_bot_token, config_data)

    try:
        # Update telegram settings
        result = db.execute_commit(
            "UPDATE radio_system_telegram_settings SET telegram_enabled = %s, telegram_bot_token = %s, telegram_channel_id = %s WHERE system_id = %s",
            (system_data.get("telegram_enabled") or 0, telegram_bot_token or None,
             system_data.get("telegram_channel_id") or None, system_data.get("system_id"))
        )
    except Exception as e:
        module_logger.error(f"Unexpected Exception when saving system telegram settings: {e}")
        result = {"success": False, "message": f"Unexpected Exception when saving system telegram settings: {e}",
                  "result": []}

    return result


def update_system_webhook_settings(db, system_data):
    try:
        result = db.execute_commit(
            "UPDATE radio_system_webhooks SET enabled = %s, webhook_url = %s, webhook_headers = %s WHERE system_id = %s",
            (system_data.get("webhook_enabled") or 0, system_data.get("webhook_url") or None,
             json.dumps(system_data.get("webhook_headers", {})), system_data.get("system_id"))
        )
    except Exception as e:
        module_logger.error(f"Unexpected Exception when saving system telegram settings: {e}")
        result = {"success": False, "message": f"Unexpected Exception when saving system telegram settings: {e}",
                  "result": []}

    return result


def delete_radio_system(db, system_id):
    if not system_id:
        module_logger.warning(f"System ID Empty")
        return {"success": False, "message": "System ID Empty", "result": []}

    check_result = check_for_system(db, system_id=system_id)
    module_logger.debug(check_result)

    query = f"DELETE FROM radio_systems WHERE system_id = %s"
    params = (int(system_id),)
    result = db.execute_commit(query, params)
    return result


def get_system_api_key(db, system_api_key):
    query = f"SELECT system_id FROM radio_systems WHERE system_api_key = %s"
    params = (system_api_key,)
    result = db.execute_query(query, params, fetch_mode="one")
    return result
