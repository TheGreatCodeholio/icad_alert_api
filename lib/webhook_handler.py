import json


def update_system_webhooks(db, system_id, webhooks_data):
    try:
        # Fetch the current webhooks from the database
        current_webhooks = {}
        get_result = db.execute_query(
            "SELECT webhook_id, webhook_url, webhook_headers, enabled FROM radio_system_webhooks WHERE system_id = %s",
            (system_id,))
        if get_result.get("success") and get_result.get("result"):
            for webhook_data in get_result.get("result"):
                current_webhooks[webhook_data.get("webhook_id")] = webhook_data

        # Process each provided webhook update or addition
        for webhook in webhooks_data:
            webhook_id = webhook.get("webhook_id")
            webhook_url = webhook.get("webhook_url")
            webhook_headers = json.dumps(webhook.get("webhook_headers", {}))  # Convert dictionary to JSON string
            enabled = 1 if webhook.get("enabled") else 0

            if webhook_id and webhook_id in current_webhooks:
                # Update existing webhook if there are changes
                if (current_webhooks[webhook_id]['webhook_url'] != webhook_url or
                        current_webhooks[webhook_id]['webhook_headers'] != webhook_headers or
                        current_webhooks[webhook_id]['enabled'] != enabled):
                    db.execute_commit(
                        "UPDATE radio_system_webhooks SET webhook_url = %s, webhook_headers = %s, enabled = %s WHERE webhook_id = %s AND system_id = %s",
                        (webhook_url, webhook_headers, enabled, webhook_id, system_id))
            else:
                # Insert new webhook if it doesn't exist
                db.execute_commit(
                    "INSERT INTO radio_system_webhooks (system_id, webhook_url, webhook_headers, enabled) VALUES (%s, %s, %s, %s)",
                    (system_id, webhook_url, webhook_headers, enabled))

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
            "SELECT webhook_id, webhook_url, webhook_headers, enabled FROM alert_trigger_webhooks WHERE trigger_id = %s",
            (trigger_id,))
        if get_result.get("success") and get_result.get("result"):
            for webhook_data in get_result.get("result"):
                current_webhooks[webhook_data.get("webhook_id")] = webhook_data

        # Process each provided webhook update or addition
        for webhook in webhooks_data:
            webhook_id = webhook.get("webhook_id")
            webhook_url = webhook.get("webhook_url")
            webhook_headers = json.dumps(webhook.get("webhook_headers", {}))  # Convert dictionary to JSON string
            enabled = 1 if webhook.get("enabled") else 0

            if webhook_id and webhook_id in current_webhooks:
                # Update existing webhook if there are changes
                if (current_webhooks[webhook_id]['webhook_url'] != webhook_url or
                        current_webhooks[webhook_id]['webhook_headers'] != webhook_headers or
                        current_webhooks[webhook_id]['enabled'] != enabled):
                    db.execute_commit(
                        "UPDATE alert_trigger_webhooks SET webhook_url = %s, webhook_headers = %s, enabled = %s WHERE webhook_id = %s AND trigger_id = %s",
                        (webhook_url, webhook_headers, enabled, webhook_id, trigger_id))
            else:
                # Insert new webhook if it doesn't exist
                db.execute_commit(
                    "INSERT INTO alert_trigger_webhooks (trigger_id, webhook_url, webhook_headers, enabled) VALUES (%s, %s, %s, %s)",
                    (trigger_id, webhook_url, webhook_headers, enabled))

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
