import json
import logging

from lib.config_handler import is_fernet_token, encrypt_password

module_logger = logging.getLogger("icad_alerting_api.alert_trigger_handler")


def check_for_trigger(db, trigger_name, system_id, trigger_id=None):
    if not trigger_id:
        query = f"SELECT * FROM alert_triggers WHERE alert_triggers.trigger_name = %s AND system_id = %s"
        params = (trigger_name, system_id)
    else:
        query = f"SELECT * FROM alert_triggers WHERE alert_triggers.trigger_id = %s AND system_id = %s"
        params = (trigger_id, system_id)

    result = db.execute_query(query, params, fetch_mode='one')
    return result.get("result", {})


def get_alert_triggers(db, system_ids=None, trigger_id=None):
    # Base query
    query = """
        SELECT at.*, 
        atps.pushover_group_token,
        atps.pushover_app_token,
        atps.pushover_subject,
        atps.pushover_body,
        atps.pushover_sound, 
        GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"webhook_id": "', tw.webhook_id, 
            '", "enabled": "', tw.enabled,
            '", "webhook_url": "', tw.webhook_url,
            '", "webhook_headers": "', tw.webhook_headers, '"}'
        ) SEPARATOR '|') AS trigger_webhooks,
        GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"email_id": "', te.email_id, 
            '", "email_address": "', te.email_address,
            '", "enabled": "', te.enabled, '"}'
        ) SEPARATOR '|') AS trigger_emails,
        GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"alert_filter_id": "', atf.alert_filter_id, 
            '", "alert_filter_name": "', atf.alert_filter_name,
            '", "enabled": "', atf.enabled, '"}'
        ) SEPARATOR '|') AS trigger_alert_filters
        FROM `alert_triggers` at
        LEFT JOIN alert_trigger_emails te ON at.trigger_id = te.trigger_id
        LEFT JOIN alert_trigger_webhooks tw ON at.trigger_id = tw.trigger_id
        LEFT JOIN icad_alerting.alert_trigger_pushover_settings atps on at.trigger_id = atps.trigger_id
        LEFT JOIN icad_alerting.alert_trigger_filters atf on at.alert_filter_id = atf.alert_filter_id
        """

    # Conditions and parameters list
    conditions = []
    params = []

    # Check if system_ids are provided and append the condition and parameter
    if system_ids:
        # Prepare a string with placeholders for system_ids (e.g., %s, %s, ...)
        placeholders = ', '.join(['%s'] * len(system_ids))
        conditions.append(f"at.system_id IN ({placeholders})")
        params.extend(system_ids)

    # Check if agency_id is provided and append the condition and parameter
    if trigger_id is not None:
        conditions.append("at.trigger_id = %s")
        params.append(trigger_id)

    # If there are conditions, append them to the query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add GROUP BY to ensure emails are aggregated per trigger
    query += " GROUP BY at.trigger_id"

    # Convert params to a tuple
    params = tuple(params)

    # Execute the query with the parameters
    result = db.execute_query(query, params)

    module_logger.debug(result.get("result"))

    # Process the result to convert trigger_emails from comma seperated json strings to list of dicts
    processed_result = []
    for row in result["result"]:
        row_dict = dict(row)

        row_dict["enable_facebook"] = bool(int(row_dict.get('enable_facebook')))
        row_dict["enable_telegram"] = bool(int(row_dict.get('enable_telegram')))

        # Type conversion for numeric and JSON fields
        if 'ignore_time' in row_dict and row_dict['ignore_time']:
            row_dict['ignore_time'] = float(row_dict['ignore_time'])
        if 'tone_tolerance' in row_dict and row_dict['tone_tolerance']:
            row_dict['tone_tolerance'] = float(row_dict['tone_tolerance'])
        if 'two_tone_a' in row_dict and row_dict['two_tone_a']:
            row_dict['two_tone_a'] = float(row_dict['two_tone_a'])
        if 'two_tone_a_length' in row_dict and row_dict['two_tone_a_length']:
            row_dict['two_tone_a_length'] = float(row_dict['two_tone_a_length'])
        if 'two_tone_b' in row_dict and row_dict['two_tone_b']:
            row_dict['two_tone_b'] = float(row_dict['two_tone_b'])
        if 'two_tone_b_length' in row_dict and row_dict['two_tone_b_length']:
            row_dict['two_tone_b_length'] = float(row_dict['two_tone_b_length'])
        if 'long_tone' in row_dict and row_dict['long_tone']:
            row_dict['long_tone'] = float(row_dict['long_tone'])
        if 'long_tone_length' in row_dict and row_dict['long_tone_length']:
            row_dict['long_tone_length'] = float(row_dict['long_tone_length'])
        if 'hi_low_tone_a' in row_dict and row_dict['hi_low_tone_a']:
            row_dict['hi_low_tone_a'] = float(row_dict['hi_low_tone_a'])
        if 'hi_low_tone_b' in row_dict and row_dict['hi_low_tone_b']:
            row_dict['hi_low_tone_b'] = float(row_dict['hi_low_tone_b'])
        if 'hi_low_alternations' in row_dict and row_dict['hi_low_tone_b']:
            row_dict['hi_low_alternations'] = int(row_dict['hi_low_alternations'])

        # Processing 'trigger_emails'
        if row_dict['trigger_emails']:
            email_items = row_dict['trigger_emails'].split('|')
            row_dict['trigger_emails'] = [json.loads(email.strip()) for email in email_items if email.strip()]
            for email in row_dict['trigger_emails']:
                email['enabled'] = bool(int(email['enabled']))  # Convert "1"/"0" to True/False
                email['email_id'] = int(email['email_id'])
        else:
            row_dict['trigger_emails'] = []

        # Processing 'trigger_webhooks'
        if row_dict['trigger_webhooks']:
            webhook_items = row_dict['trigger_webhooks'].split('|')
            row_dict['trigger_webhooks'] = [json.loads(webhook.strip()) for webhook in webhook_items if webhook.strip()]
            for webhook in row_dict['trigger_webhooks']:
                webhook['enabled'] = bool(int(webhook['enabled']))
                webhook['webhook_id'] = int(webhook['webhook_id'])
                webhook['webhook_headers'] = json.loads(webhook['webhook_headers'])  # Assuming this should be a dict
        else:
            row_dict['trigger_webhooks'] = []

        # Processing 'trigger_alert_filters'
        if row_dict['trigger_alert_filters']:
            alert_filter_items = row_dict['trigger_alert_filters'].split('|')
            row_dict['trigger_alert_filters'] = [json.loads(alert_filter.strip()) for alert_filter in alert_filter_items if alert_filter.strip()]
            for alert_filter in row_dict['trigger_alert_filters']:
                alert_filter['enabled'] = bool(int(alert_filter['enabled']))
                alert_filter['alert_filter_name'] = alert_filter['alert_filter_name']
                alert_filter['alert_filter_id'] = int(alert_filter['alert_filter_id'])
        else:
            row_dict['trigger_alert_filters'] = []

        processed_result.append(row_dict)

    result["result"] = processed_result

    return result


def add_alert_trigger(db, trigger_data):
    check_result = check_for_trigger(db, trigger_data.get('trigger_name'), trigger_data.get('system_id'))
    if check_result:
        module_logger.warning(f"Trigger with that name already exists: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger with that name already exists: {trigger_data.get('trigger_name')}", "result": []}

    enabled = 1 if trigger_data.get("enabled") else 0

    query = (f'INSERT INTO alert_triggers (system_id, trigger_name, '
             f'two_tone_a, two_tone_a_length, two_tone_b, two_tone_b_length, '
             f'long_tone, long_tone_length, hi_low_tone_a, hi_low_tone_b, hi_low_alternations,'
             f'alert_filter_id, tone_tolerance, ignore_time, stream_url, enable_facebook, enable_telegram, enabled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' )
    params = (trigger_data.get('system_id'),
              trigger_data.get('trigger_name'),
              trigger_data.get('two_tone_a') or None, trigger_data.get('two_tone_a_length') or None,
              trigger_data.get('two_tone_b') or None, trigger_data.get('two_tone_b_length') or None,
              trigger_data.get('long_tone') or None, trigger_data.get('long_tone_length') or None,
              trigger_data.get('hi_low_tone_a') or None, trigger_data.get('hi_low_tone_b') or None,
              trigger_data.get('hi_low_alternations', 4),
              trigger_data.get('alert_filter_id') or None, trigger_data.get('tone_tolerance', 2.0),
              trigger_data.get('ignore_time', 300.0), trigger_data.get('stream_url') or None,
              0, 0, enabled)

    result = db.execute_commit(query, params)

    if result.get("success"):
        insert_alert_trigger_default(db, trigger_data)

    return result


def insert_alert_trigger_default(db, trigger_data):
    db.execute_commit(
        "INSERT INTO alert_trigger_pushover_settings (trigger_id) VALUES (%s)",
        (trigger_data.get('trigger_id'),)
    )


def delete_alert_trigger(db, system_id, trigger_id):
    if not system_id or not trigger_id:
        module_logger.warning(f"System ID or Trigger ID Empty")
        return {"success": False, "message": "System ID or Trigger ID Empty", "result": []}

    check_result = check_for_trigger(db, "None", system_id, trigger_id)

    if not check_result:
        return {"success": False, "message": "Trigger Doesn't Exist", "result": []}

    query = f"DELETE FROM alert_triggers WHERE system_id = %s and trigger_id = %s"
    params = (system_id, trigger_id)
    result = db.execute_commit(query, params)
    return result


def update_alert_trigger_general(db, trigger_data):
    if not trigger_data:
        module_logger.warning(f"No trigger data provided")
        return {"success": False,
                "message": f"No trigger data provided", "result": []}

    if not trigger_data.get('trigger_name'):
        module_logger.warning(f"Trigger name can not be empty.")
        return {"success": False,
                "message": f"Trigger name can not be empty.", "result": []}

    check_result = check_for_trigger(db, trigger_data.get("trigger_name"), trigger_data.get('system_id'),
                                     trigger_data.get('trigger_id'))
    if not check_result:
        module_logger.warning(f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}", "result": []}

    enabled = 1 if trigger_data.get("enabled") else 0
    facebook_enabled = 1 if trigger_data.get("enable_facebook") else 0
    telegram_enabled = 1 if trigger_data.get("enable_telegram") else 0

    query = f"UPDATE alert_triggers SET trigger_name = %s, tone_tolerance = %s, ignore_time = %s, stream_url = %s, enable_facebook = %s, enable_telegram = %s, enabled = %s WHERE system_id = %s AND trigger_id = %s"
    params = (trigger_data.get('trigger_name'), trigger_data.get('tone_tolerance', 2.0),
              trigger_data.get('ignore_time', 300.0), trigger_data.get('stream_url') or None,
              facebook_enabled, telegram_enabled,
              enabled , trigger_data.get('system_id'), trigger_data.get('trigger_id'))

    update_result = db.execute_commit(query, params)
    return update_result


def update_alert_trigger_two_tone(db, trigger_data):
    if not trigger_data:
        module_logger.warning(f"No trigger data provided")
        return {"success": False,
                "message": f"No trigger data provided", "result": []}

    if not trigger_data.get('trigger_name'):
        module_logger.warning(f"Trigger name can not be empty.")
        return {"success": False,
                "message": f"Trigger name can not be empty.", "result": []}

    check_result = check_for_trigger(db, trigger_data.get("trigger_name"), trigger_data.get('system_id'),
                                     trigger_data.get('trigger_id'))
    if not check_result:
        module_logger.warning(f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}", "result": []}

    query = f"UPDATE alert_triggers SET two_tone_a = %s, two_tone_a_length = %s, two_tone_b = %s, two_tone_b_length = %s WHERE system_id = %s AND trigger_id = %s"
    params = (trigger_data.get('two_tone_a') or None, trigger_data.get('two_tone_a_length', 0.8),
              trigger_data.get('two_tone_b') or None, trigger_data.get('two_tone_b_length', 2.8),
              trigger_data.get('system_id'), trigger_data.get('trigger_id'))

    update_result = db.execute_commit(query, params)
    return update_result


def update_alert_trigger_long_tone(db, trigger_data):
    if not trigger_data:
        module_logger.warning(f"No trigger data provided")
        return {"success": False,
                "message": f"No trigger data provided", "result": []}

    if not trigger_data.get('trigger_name'):
        module_logger.warning(f"Trigger name can not be empty.")
        return {"success": False,
                "message": f"Trigger name can not be empty.", "result": []}

    check_result = check_for_trigger(db, trigger_data.get("trigger_name"), trigger_data.get('system_id'),
                                     trigger_data.get('trigger_id'))
    if not check_result:
        module_logger.warning(f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}", "result": []}

    query = f"UPDATE alert_triggers SET long_tone = %s, long_tone_length = %s WHERE system_id = %s AND trigger_id = %s"
    params = (trigger_data.get('long_tone') or None, trigger_data.get('long_tone_length', 4.8),
              trigger_data.get('system_id'), trigger_data.get('trigger_id'))

    update_result = db.execute_commit(query, params)
    return update_result


def update_alert_trigger_hi_low_tone(db, trigger_data):
    if not trigger_data:
        module_logger.warning(f"No trigger data provided")
        return {"success": False,
                "message": f"No trigger data provided", "result": []}

    if not trigger_data.get('trigger_name'):
        module_logger.warning(f"Trigger name can not be empty.")
        return {"success": False,
                "message": f"Trigger name can not be empty.", "result": []}

    check_result = check_for_trigger(db, trigger_data.get("trigger_name"), trigger_data.get('system_id'),
                                     trigger_data.get('trigger_id'))
    if not check_result:
        module_logger.warning(f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}", "result": []}

    query = f"UPDATE alert_triggers SET hi_low_tone_a = %s, hi_low_tone_b = %s, hi_low_alternations = %s WHERE system_id = %s AND trigger_id = %s"
    params = (trigger_data.get('hi_low_tone_a') or None, trigger_data.get('hi_low_tone_b') or None,
              trigger_data.get('hi_low_alternations', 4),
              trigger_data.get('system_id'), trigger_data.get('trigger_id'))

    update_result = db.execute_commit(query, params)
    return update_result


def update_alert_trigger_alert_filter(db, trigger_data):
    if not trigger_data:
        module_logger.warning(f"No trigger data provided")
        return {"success": False,
                "message": f"No trigger data provided", "result": []}

    if not trigger_data.get('trigger_name'):
        module_logger.warning(f"Trigger name can not be empty.")
        return {"success": False,
                "message": f"Trigger name can not be empty.", "result": []}

    check_result = check_for_trigger(db, trigger_data.get("trigger_name"), trigger_data.get('system_id'),
                                     trigger_data.get('trigger_id'))
    if not check_result:
        module_logger.warning(f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}", "result": []}
    alert_filter_id = None if trigger_data.get('alert_filter_id') == "0" else trigger_data.get('alert_filter_id')
    query = f"UPDATE alert_triggers SET alert_filter_id = %s WHERE system_id = %s AND trigger_id = %s"
    params = (alert_filter_id or None,
              trigger_data.get('system_id'), trigger_data.get('trigger_id'))

    update_result = db.execute_commit(query, params)
    return update_result


def update_trigger_alert_emails(db, trigger_id, emails_data):
    try:
        # Fetch the current emails from the database
        current_emails = {}
        get_result = db.execute_query(
            "SELECT email_id, email_address, enabled FROM alert_trigger_emails WHERE trigger_id = %s",
            (trigger_id,))
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
                        "UPDATE alert_trigger_emails SET email_address = %s, enabled = %s WHERE email_id = %s AND trigger_id = %s",
                        (email_address, enabled, email_id, trigger_id))
            else:
                # Insert new email if it doesn't exist
                db.execute_commit(
                    "INSERT INTO alert_trigger_emails (trigger_id, email_address, enabled) VALUES (%s, %s, %s)",
                    (trigger_id, email_address, enabled))

        # Check for emails to remove
        existing_ids = set(current_emails.keys())
        provided_ids = {email.get("email_id") for email in emails_data if email.get("email_id")}
        ids_to_remove = existing_ids - provided_ids

        for email_id in ids_to_remove:
            db.execute_commit("DELETE FROM alert_trigger_emails WHERE trigger_id = %s AND email_id = %s",
                              (trigger_id, email_id))

        result = {"success": True, "message": "Emails updated successfully."}
    except Exception as e:
        result = {"success": False, "message": f"Failed to update emails: {e}"}

    return result


def update_alert_trigger_pushover(db, trigger_data, config_data):
    pushover_group_token = trigger_data.get("pushover_group_token")
    pushover_app_token = trigger_data.get("pushover_app_token")

    if pushover_group_token is not None:
        if not is_fernet_token(pushover_group_token, config_data):
            pushover_group_token = encrypt_password(pushover_group_token, config_data)

    if pushover_app_token is not None:
        if not is_fernet_token(pushover_app_token, config_data):
            pushover_app_token = encrypt_password(pushover_app_token, config_data)

    if not trigger_data:
        module_logger.warning(f"No trigger data provided")
        return {"success": False,
                "message": f"No trigger data provided", "result": []}

    if not trigger_data.get('trigger_name'):
        module_logger.warning(f"Trigger name can not be empty.")
        return {"success": False,
                "message": f"Trigger name can not be empty.", "result": []}

    check_result = check_for_trigger(db, trigger_data.get("trigger_name"), trigger_data.get('system_id'),
                                     trigger_data.get('trigger_id'))
    if not check_result:
        module_logger.warning(f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}")
        return {"success": False,
                "message": f"Trigger Doesn't Exist: {trigger_data.get('trigger_name')}", "result": []}

    query = f"UPDATE alert_trigger_pushover_settings SET pushover_group_token = %s, pushover_app_token = %s, pushover_subject = %s, pushover_body = %s, pushover_sound = %s WHERE trigger_id = %s"
    params = (pushover_group_token or None, pushover_app_token or None,
              trigger_data.get('pushover_subject') or None, trigger_data.get('pushover_body') or None,
              trigger_data.get('pushover_sound') or None, trigger_data.get('trigger_id'))

    update_result = db.execute_commit(query, params)

    return update_result
