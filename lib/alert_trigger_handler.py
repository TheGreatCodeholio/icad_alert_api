import json
import logging

module_logger = logging.getLogger("icad_alerting_api.alert_trigger_handler")


def get_alert_triggers(db, system_ids=None, trigger_id=None):
    # Base query
    query = """
        SELECT at.*, GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"webhook_id": "', tw.trigger_webhook_id, 
            '", "enabled": "', tw.webhook_enabled,
            '", "webhook_url": "', tw.webhook_url,
            '", "webhook_headers": "', tw.webhook_headers, '"}'
        ) SEPARATOR '|') AS trigger_webhooks,
        GROUP_CONCAT(
        DISTINCT CONCAT(
            '{"trigger_email_id": "', te.trigger_email_id, 
            '", "email_address": "', te.email_address,
            '", "enabled": "', te.email_enabled, '"}'
        ) SEPARATOR '|') AS trigger_emails
        FROM `alert_triggers` at
        LEFT JOIN alert_trigger_emails te ON at.trigger_id = te.trigger_id
        LEFT JOIN alert_trigger_webhooks tw ON at.trigger_id = tw.trigger_id
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

        # Type conversion for numeric and JSON fields
        if 'ignore_time' in row_dict and row_dict['ignore_time']:
            row_dict['ignore_time'] = float(row_dict['ignore_time'])
        if 'two_tone_a' in row_dict and row_dict['two_tone_a']:
            row_dict['two_tone_a'] = float(row_dict['two_tone_a'])
        if 'two_tone_b' in row_dict and row_dict['two_tone_b']:
            row_dict['two_tone_b'] = float(row_dict['two_tone_b'])
        if 'long_tone' in row_dict and row_dict['long_tone']:
            row_dict['long_tone'] = float(row_dict['long_tone'])
        if 'hi_low_tone_a' in row_dict and row_dict['hi_low_tone_a']:
            row_dict['hi_low_tone_a'] = float(row_dict['hi_low_tone_a'])
        if 'hi_low_tone_b' in row_dict and row_dict['hi_low_tone_b']:
            row_dict['hi_low_tone_b'] = float(row_dict['hi_low_tone_b'])

        # Processing 'trigger_emails'
        if row_dict['trigger_emails']:
            email_items = row_dict['trigger_emails'].split('|')
            row_dict['trigger_emails'] = [json.loads(email.strip()) for email in email_items if email.strip()]
            for email in row_dict['trigger_emails']:
                email['enabled'] = bool(int(email['enabled']))  # Convert "1"/"0" to True/False
                email['trigger_email_id'] = int(email['trigger_email_id'])

        # Processing 'trigger_webhooks'
        if row_dict['trigger_webhooks']:
            webhook_items = row_dict['trigger_webhooks'].split('|')
            row_dict['trigger_webhooks'] = [json.loads(webhook.strip()) for webhook in webhook_items if webhook.strip()]
            for webhook in row_dict['trigger_webhooks']:
                webhook['enabled'] = bool(int(webhook['enabled']))
                webhook['webhook_id'] = int(webhook['webhook_id'])
                webhook['webhook_headers'] = json.loads(webhook['webhook_headers'])  # Assuming this should be a dict

        processed_result.append(row_dict)

    result["result"] = processed_result

    return result
