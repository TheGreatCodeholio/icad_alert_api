import logging


from lib.alert_trigger_handler import get_alert_triggers

module_logger = logging.getLogger("icad_tone_detection.system_handler")


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
    rs.
FROM radio_systems rs
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
        final_query = f"{base_query} {where_clause}"
    else:
        final_query = base_query

    systems_result = db.execute_query(final_query, tuple(parameters) if parameters else None)
    if not systems_result.get("success"):
        module_logger.error("Systems Result Empty")

    if with_triggers:
        for system in systems_result['result']:
            trigger_result = get_alert_triggers(db, system_ids=[system.get('system_id')], trigger_id=None)
            if not trigger_result.get("success"):
                module_logger.warning("Trigger Result Empty")
                system["alert_triggers"] = []
            # Add the systems triggers to the system data.
            system["alert_triggers"] = trigger_result['result'] if trigger_result['result'] else []
    else:
        for system in systems_result['result']:
            system["alert_triggers"] = []

    return systems_result
