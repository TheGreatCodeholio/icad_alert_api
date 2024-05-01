import logging
import time

import redis

module_logger = logging.getLogger('icad_alerting_api.alert_processing')


def process_call_data(db, rd, system_data, call_data):
    process_result = {"tone_result": [], "transcript_filter": []}
    tone_result = check_tone_triggers(rd, system_data, call_data)
    if len(tone_result) >= 1:
        process_result["tone_result"] = tone_result

    return process_result


def get_tolerance(trigger, tone_key):
    """Calculate the tolerance for a tone."""
    return trigger.get("tone_tolerance", 2) / 100.0 * trigger.get(tone_key)


def is_within_range(tone, tone_range):
    """Check if the tone is within the given range."""
    return tone_range[0] <= tone <= tone_range[1]


def are_all_tone_conditions_met(conditions_required, conditions_met):
    # Check each condition in conditions_required
    for condition, is_required in conditions_required.items():
        # If it's required but not met, return False
        if is_required and not conditions_met[condition]:
            return False
    # If all required conditions are met, return True
    return True


def check_tone_triggers(rd, system_data, call_data):
    triggered_alerts = []

    alert_triggers = system_data.get('alert_triggers')
    if not len(alert_triggers):
        module_logger.debug("No Alert Triggers in System Data. Skipping Tone Check")
        return triggered_alerts

    # Get the list of excluded trigger ids once for this system
    triggered_alert_list = get_active_alerts_cache(rd, f"icad_current_alerts:{call_data.get('short_name')}")
    excluded_id_list = [t["trigger_id"] for t in triggered_alert_list]

    for trigger in alert_triggers:
        alert_data = {"two_tone": [], "long_tone": [], "hi_low_tone": []}
        if trigger.get("trigger_id") in excluded_id_list:
            module_logger.warning(f"Ignoring {trigger.get('trigger_name')}")
            continue

        conditions_required = {
            "two_tone": True if trigger.get('two_tone_a') is not None and trigger.get(
                'two_tone_b') is not None else False,
            "long_tone": True if trigger.get('long_tone') is not None else False,
            "hi_low_tone": True if trigger.get('hi_low_tone_a') is not None and trigger.get(
                'hi_low_tone_b') is not None else False
        }
        conditions_met = {"two_tone": False, "long_tone": False, "hi_low_tone": False}

        # Check if no conditions are required
        if not any(conditions_required.values()):
            module_logger.debug(f"Skipping tone alert trigger {trigger.get('trigger_name')}. No conditions required.")
            continue

        two_tone_matches = check_two_tone_triggers(trigger, call_data)
        if len(two_tone_matches) >= 1:
            conditions_met["two_tone"] = True
            alert_data["two_tone"].extend(two_tone_matches)

        long_tone_matches = check_long_tone_triggers(trigger, call_data)
        if len(long_tone_matches) >= 1:
            conditions_met["long_tone"] = True
            alert_data["long_tone"].extend(long_tone_matches)

        high_low_matches = check_hi_low_tone_triggers(trigger, call_data)
        if len(high_low_matches) >= 1:
            conditions_met["hi_low_tone"] = True
            alert_data["hi_low_tone"].extend(high_low_matches)

        all_conditions_met = are_all_tone_conditions_met(conditions_required, conditions_met)
        if all_conditions_met:
            module_logger.info(f"Alert triggered for {trigger.get('trigger_name')}")
            active_dict = {
                "last_detected": time.time(),
                "ignore_seconds": trigger.get("ignore_time", 300),
                "trigger_id": trigger.get("trigger_id")
            }
            add_active_alerts_cache(rd, f"icad_current_alerts:{call_data.get('short_name')}", active_dict)
            excluded_id_list.append(trigger.get("trigger_id"))
            triggered_alerts.append(alert_data)

            # Start Alerting Process For Tones

    return triggered_alerts


def check_two_tone_triggers(alert_trigger, call_data):
    matches_found = []

    # Simplify the extraction of match_list
    match_list = [(tone['detected'][0], tone['detected'][1], tone["tone_id"])
                  for tone in call_data.get("tones", {}).get("two_tone", [])]

    a_tone, b_tone = alert_trigger.get("two_tone_a"), alert_trigger.get("two_tone_b")
    # Skip the trigger if either two_tone_a or tow_tone_b is missing
    if not a_tone or not b_tone:
        return matches_found

    tolerance_a, tolerance_b = get_tolerance(alert_trigger, "two_tone_a"), get_tolerance(alert_trigger, "two_tone_b")
    detector_ranges = [(a_tone - tolerance_a, a_tone + tolerance_a), (b_tone - tolerance_b, b_tone + tolerance_b)]

    # tone_a_length = alert_trigger.get("two_tone_a_length", 0.8)
    # tone_b_length = alert_trigger.get("two_tone_b_length", 2.3)

    for tone in match_list:
        match_a, match_b = is_within_range(tone[0], detector_ranges[0]), is_within_range(tone[1],
                                                                                         detector_ranges[1])

        if match_a and match_b:
            match_data = {
                "tone_id": tone[2],
                "trigger_name": alert_trigger.get('trigger_name'),
                "tones_matched": f'{tone[0]}, {tone[1]}'
            }

            matches_found.append(match_data)

            module_logger.debug(f"Two Tone Match found for {alert_trigger.get('trigger_name')}")

    return matches_found


def check_long_tone_triggers(alert_trigger, call_data):
    matches_found = []

    # Extract long_tone details
    match_list = [(tone['detected'], tone["tone_id"])
                  for tone in call_data.get("tones", {}).get("long_tone", [])]

    long_tone = alert_trigger.get("long_tone")
    if not long_tone:
        return matches_found

    tolerance = get_tolerance(alert_trigger, "long_tone")
    required_length = alert_trigger.get("long_tone_length", 0)
    tone_range = (long_tone - tolerance, long_tone + tolerance)

    for tone in match_list:
        match_tone = is_within_range(tone[0], tone_range)

        if match_tone:
            match_data = {
                "tone_id": tone[1],
                "trigger_name": alert_trigger.get('trigger_name'),
                "tones_matched": f'{tone[0]}'
            }

            matches_found.append(match_data)

            module_logger.debug(f"Match found for {alert_trigger.get('trigger_name')}")

    return matches_found


def check_hi_low_tone_triggers(alert_trigger, call_data):
    matches_found = []

    # Extract high-low tones detected from call_data
    match_list = [(tone['detected'][0], tone['detected'][1], tone["tone_id"])
                  for tone in call_data.get("tones", {}).get("hl_tone", [])]

    hi_tone, low_tone = alert_trigger.get("hi_low_tone_a"), alert_trigger.get("hi_low_tone_b")
    if not hi_tone or not low_tone:
        return matches_found

    tolerance_hi, tolerance_low = get_tolerance(alert_trigger, "hi_low_tone_a"), get_tolerance(alert_trigger,
                                                                                               "hi_low_tone_b")
    tone_range = [(hi_tone - tolerance_hi, hi_tone + tolerance_hi),
                  (low_tone - tolerance_low, low_tone + tolerance_low)]

    for tone in match_list:
        match_hi, match_low = is_within_range(tone[0], tone_range[0]), is_within_range(tone[1],
                                                                                       tone_range[1])

        if match_hi and match_low:
            match_data = {
                "tone_id": tone[2],
                "trigger_name": alert_trigger.get('trigger_name'),
                "tones_matched": f'{tone[0]}, {tone[1]}'
            }

            matches_found.append(match_data)

            module_logger.debug(f"Match found for {alert_trigger.get('trigger_name')}")

    return matches_found


def add_active_alerts_cache(rd, list_name, dict_data):
    """
    Add a dictionary to a Redis list.

    Args:
        rd (RedisCache): An instance of the RedisCache class.
        list_name (str): The name of the Redis list.
        dict_data (dict): The dictionary to add to the list.

    Returns:
        bool: True if successful, False otherwise.
    """

    try:
        rd.rpush(list_name, dict_data)
        return True
    except redis.RedisError as error:
        module_logger.error(f"Error adding dict to list {list_name}: {error}")
        return False


def delete_active_alerts_cache(rd, list_name):
    """
    Clear a Redis list.

    Args:
        rd (RedisCache): An instance of the RedisCache class.
        list_name (str): The name of the Redis list to clear.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        rd.delete(list_name)
        return True
    except redis.RedisError as error:
        module_logger.error(f"Error clearing list {list_name}: {error}")
        return False


def get_active_alerts_cache(rd, list_name):
    """
    Get all dictionaries from a Redis list.

    Args:
        rd (RedisCache): An instance of the RedisCache class.
        list_name (str): The name of the Redis list.

    Returns:
        list: A list of dictionaries, or an empty list if an error occurs.
    """
    try:
        result = rd.lrange(list_name, 0, -1)
        if result['success']:
            return result.get("result", [])
        else:
            return []
    except redis.RedisError as error:
        module_logger.error(f"Error retrieving list {list_name}: {error}")
        return []
