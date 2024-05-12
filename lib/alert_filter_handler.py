import json
import logging

module_logger = logging.getLogger("icad_alerting_api.alert_filter_handler")


def check_for_filter(db, filter_id):
    query = f"SELECT * FROM alert_trigger_filters WHERE alert_filter_id = %s"
    params = (filter_id,)

    result = db.execute_query(query, params, fetch_mode='one')
    return result.get("result", {})


def get_alert_filters(db, alert_filter_id=None):
    base_query = """
    SELECT af.*,
    GROUP_CONCAT(
        DISTINCT `CONCAT`(
            '{"keyword_id": "', atfk.keyword_id,
            '", "alert_filter_id": "', atfk.alert_filter_id,
            '", "keyword": "', atfk.keyword,
            '", "is_excluded": "', atfk.is_excluded, 
            '", "enabled": "', atfk.enabled, '"}'
        ) SEPARATOR '|') AS filter_keywords
    FROM alert_trigger_filters as af
    LEFT JOIN icad_alerting.alert_trigger_filter_keywords atfk on af.alert_filter_id = atfk.alert_filter_id
    """

    parameters = []
    if alert_filter_id:
        parameters.append(alert_filter_id)
        final_query = f"{base_query} AND af.alert_filter_id = %s"
    else:
        final_query = f"{base_query} GROUP BY af.alert_filter_id"

    filters_result = db.execute_query(final_query, tuple(parameters) if parameters else None)
    if not filters_result.get("success"):
        module_logger.error("Alert Filter Result Empty")
        return filters_result

    for filter in filters_result.get("result"):
        module_logger.debug(filter)
        # Processing 'filter_keywords'
        if filter['filter_keywords']:
            keyword_items = filter['filter_keywords'].split('|')
            filter['filter_keywords'] = [json.loads(keyword.strip()) for keyword in keyword_items if keyword.strip()]
            for keyword in filter['filter_keywords']:
                module_logger.debug(keyword)
                keyword['keyword_id'] = int(keyword['keyword_id'])
                keyword['alert_filter_id'] = int(keyword['alert_filter_id'])
                keyword['keyword'] = keyword['keyword']
                keyword['is_excluded'] = bool(int(keyword['is_excluded']))
                keyword['enabled'] = bool(int(keyword['enabled']))
        else:
            filter['filter_keywords'] = []

    return filters_result


def add_filter(db, filter_data):
    if not filter_data.get('alert_filter_name'):
        module_logger.warning(f"Filter Name Empty")
        return {"success": False, "message": "Filter name can not be Empty", "result": []}

    enabled = 1 if filter_data.get("enabled") else 0

    query = f"INSERT INTO alert_trigger_filters (alert_filter_name, enabled) VALUES (%s, %s)"
    params = (filter_data.get('alert_filter_name'), enabled)

    result = db.execute_commit(query, params)
    return result


def delete_filter(db, filter_id):
    if not filter_id:
        module_logger.warning(f"Filter ID Empty")
        return {"success": False, "message": "Filter ID Empty", "result": []}

    check_result = check_for_filter(db, filter_id)

    if not check_result:
        return {"success": False, "message": "Filter Doesn't Exist", "result": []}

    query = f"DELETE FROM alert_trigger_filters WHERE alert_filter_id = %s"
    params = (filter_id,)
    result = db.execute_commit(query, params)
    return result


def update_alert_filter_general(db, filter_data):
    if not filter_data.get('alert_filter_id'):
        module_logger.warning(f"Filter ID Empty")
        return {"success": False, "message": "Filter ID Empty", "result": []}

    check_result = check_for_filter(db, filter_data.get('alert_filter_id'))

    if not check_result:
        return {"success": False, "message": "Filter Doesn't Exist", "result": []}

    enabled = 1 if filter_data.get("enabled") else 0

    query = f"UPDATE alert_trigger_filters SET alert_filter_name = %s, enabled = %s WHERE alert_filter_id = %s"
    params = (filter_data.get('alert_filter_name'), enabled, filter_data.get('alert_filter_id'))
    result = db.execute_commit(query, params)
    return result


def update_filter_keyword(db, alert_filter_id, alert_filter_name, keywords_data):
    try:
        # Fetch the current webhooks from the database
        current_keywords = {}
        get_result = db.execute_query(
            "SELECT keyword_id, keyword, is_excluded, enabled FROM alert_trigger_filter_keywords WHERE alert_filter_id = %s",
            (alert_filter_id,))

        if get_result.get("success") and get_result.get("result"):
            for keyword_data in get_result.get("result"):
                current_keywords[keyword_data.get("keyword_id")] = keyword_data

        # Process each provided webhook update or addition
        for keyword in keywords_data:
            keyword_id = keyword.get("keyword_id")
            keyword_keyword = keyword.get("keyword")
            is_excluded = 1 if keyword.get("is_excluded") else 0
            enabled = 1 if keyword.get("enabled") else 0

            if keyword_id and keyword_id in current_keywords:
                # Update existing webhook if there are changes
                if (current_keywords[keyword_id]['keyword'] != keyword_keyword or
                        current_keywords[keyword_id]['is_excluded'] != is_excluded or
                        current_keywords[keyword_id]['enabled'] != enabled):
                    db.execute_commit(
                        "UPDATE alert_trigger_filter_keywords SET keyword = %s, is_excluded = %s, enabled = %s WHERE keyword_id = %s AND alert_filter_id = %s",
                        (keyword_keyword, is_excluded, enabled, keyword_id, alert_filter_id))
            else:
                # Insert new webhook if it doesn't exist
                db.execute_commit(
                    "INSERT INTO alert_trigger_filter_keywords (alert_filter_id, keyword, is_excluded, enabled) VALUES (%s, %s, %s, %s)",
                    (alert_filter_id, keyword_keyword, is_excluded, enabled))

        # Check for webhooks to remove
        existing_ids = set(current_keywords.keys())
        provided_ids = {keyword.get("keyword_id") for keyword in keywords_data if keyword.get("keyword_id")}
        ids_to_remove = existing_ids - provided_ids

        for keyword_id in ids_to_remove:
            db.execute_commit(
                "DELETE FROM alert_trigger_filter_keywords WHERE keyword_id = %s AND alert_filter_id = %s",
                (keyword_id, alert_filter_id))

        result = {"success": True, "message": f"{alert_filter_name} Keywords updated successfully."}
    except Exception as e:
        result = {"success": False, "message": f"Failed to update alert filter keywords for {alert_filter_name}: {e}"}

    return result
