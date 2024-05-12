import logging

module_logger = logging.getLogger('icad_alerting_api.alert_actions')


def run_trigger_actions(db, rd, trigger_config, call_data):
    module_logger.info(f"Running Trigger Actions for {trigger_config.get('trigger_name')}")
    # Send Alert Emails
    # Send Trigger Alert Pushover
    # Send to Trigger Webhooks
    pass


def run_global_actions(db, rd, system_config, call_data):
    module_logger.info(f"Running System Actions for {system_config.get('system_name')}")
    # Send Alert Emails
    # Send Global Alert Pushover
    # Send Alert Facebook
    # Send Alert Telegram
    # Send to System Webhooks
    pass
