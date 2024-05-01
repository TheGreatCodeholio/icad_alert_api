import os
from threading import Event, Thread
import time

import redis
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from flask_session import Session

from lib.alert_processing_handler import get_active_alerts_cache, delete_active_alerts_cache, process_call_data
from lib.alert_trigger_handler import get_alert_triggers
from lib.config_handler import load_config_file
from lib.logging_handler import CustomLogger
from lib.mysql_handler import MySQLDatabase
from lib.redis_handler import RedisCache
from lib.system_handler import get_systems

app_name = "icad_alerting_api"

log_level = 1

root_path = os.getcwd()
config_file = 'config.json'
log_path = os.path.join(root_path, 'log')
log_file_name = f"{app_name}.log"
config_path = os.path.join(root_path, 'etc')

stop_signals = {}

if not os.path.exists(log_path):
    os.makedirs(log_path)

if not os.path.exists(config_path):
    os.makedirs(config_path)

logging_instance = CustomLogger(log_level, f'{app_name}',
                                os.path.join(log_path, log_file_name))

try:
    config_data = load_config_file(os.path.join(config_path, config_file))
    logging_instance.set_log_level(config_data["log_level"])
    logger = logging_instance.logger
    logger.info("Loaded Config File")
except Exception as e:
    print(f'Error while <<loading>> configuration : {e}')
    exit(1)

if not config_data:
    logger.error('Failed to load configuration.')
    exit(1)

try:
    db = MySQLDatabase(config_data)
    logger.info("MySQL Database Connection Pool connected successfully.")
except Exception as e:
    logger.error(f'Error while <<connecting>> to the <<MySQL Database:>> {e}')
    exit(1)

try:
    rd = RedisCache(config_data)
    logger.info("Redis Pool Connection Pool connected successfully.")
except Exception as e:
    logger.error(f'Error while <<connecting>> to the <<Redis Cache:>> {e}')
    exit(1)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Session Configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host=config_data["redis"]["host"],
                                                password=config_data["redis"]["password"],
                                                port=config_data["redis"]["port"], db=3)

# Cookie Configuration
app.config['SESSION_COOKIE_SECURE'] = config_data["general"]["cookie_secure"]
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = config_data["general"]["cookie_domain"]
app.config['SESSION_COOKIE_NAME'] = config_data["general"]["cookie_name"]
app.config['SESSION_COOKIE_PATH'] = config_data["general"]["cookie_path"]
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initializing the session
sess = Session()
sess.init_app(app)


# Loop to run that clears old detections.
def clear_old_items(system_short_name):
    logger.info(f"Starting Clear Loop for {system_short_name}")
    stop_signal = stop_signals.get(system_short_name, Event())
    while not stop_signal.is_set():
        time.sleep(1)  # Sleep to prevent a tight loop that hogs the CPU

        # Fetch the current list of detections
        qc_detector_list = get_active_alerts_cache(rd, f"icad_current_alerts:{system_short_name}")
        current_time = time.time()
        if len(qc_detector_list) == 0:
            # logger.warning(f"Empty Detector List")
            continue  # Skip this iteration if list is empty

        updated_list = []
        for item in qc_detector_list:
            # Calculate the expiration time for each item
            expire_time = item['last_detected'] + item['ignore_seconds']
            if current_time < expire_time:
                # If the item hasn't expired, add it to the updated list
                updated_list.append(item)

        # If the updated list is shorter, some items were removed
        if len(updated_list) < len(qc_detector_list):
            logger.warning(f"Removing {len(qc_detector_list) - len(updated_list)}")
            # Clear the old list
            delete_active_alerts_cache(rd, f"icad_current_alerts:{system_short_name}")

            # Add the updated items back, if any
            if updated_list:
                # Push all items at once to the list
                rd.lpush(f"icad_current_alerts:{system_short_name}", *updated_list)

    logger.info(f"Stopped Clear Loop for {system_short_name}")


@app.route('/', methods=['GET'])
def index():
    logger.debug(session)
    return render_template("index.html")


# Endpoint to receive the JSON file with the audio URL
@app.route('/process_alert', methods=['POST'])
def process_alert():
    call_data = request.get_json()
    result = {
        "success": False,
        "message": "Unknown Error",
        "result": []
    }
    if call_data:
        system_data = get_systems(db, system_short_name=call_data.get('short_name'))
        if system_data.get('success') and system_data.get("result", {}):
            ## Start alert check to see if we match any of the alert triggers
            process_result = process_call_data(db, rd, system_data.get("result")[0], call_data)
            result["success"] = True
            result["message"] = "Alert Triggers Checked."
            result["result"] = process_result
            return jsonify(result), 200
        else:
            result["message"] = f"Unable to retrieve system data for {call_data.get('short_name')}"
            return jsonify(result), 400
    else:
        result["message"] = "Call data not provided"
        return jsonify(result), 400


@app.route("/api/get_triggers")
def api_get_triggers():
    system_id = request.args.get('system_id', None)
    trigger_id = request.args.get('trigger_id', None)

    system_data_result = get_alert_triggers(db, system_id, trigger_id)

    return jsonify(system_data_result)


@app.route("/api/get_systems")
def api_get_systems():
    system_id = request.args.get('system_id', None)
    with_triggers = request.args.get('with_triggers', False)

    # Fetch system data once
    system_data_result = get_systems(db, system_id, with_triggers=with_triggers)

    return jsonify(system_data_result)


systems = get_systems(db)
for system in systems.get("result"):
    system_name = system.get("system_short_name")
    if system_name not in stop_signals:
        stop_signals[system_name] = Event()
    Thread(target=clear_old_items, args=(system_name,), daemon=True).start()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8002, debug=False)
