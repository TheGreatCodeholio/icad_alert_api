import json
import os
from functools import wraps
from threading import Event, Thread
import time

import redis
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from flask_session import Session

from werkzeug.middleware.proxy_fix import ProxyFix

from lib.alert_filter_handler import get_alert_filters, delete_filter, update_alert_filter_general, \
    update_filter_keyword, add_filter
from lib.alert_processing_handler import get_active_alerts_cache, delete_active_alerts_cache, process_call_data
from lib.alert_trigger_handler import get_alert_triggers, add_alert_trigger, delete_alert_trigger, \
    update_alert_trigger_general, update_alert_trigger_long_tone, update_alert_trigger_two_tone, \
    update_alert_trigger_hi_low_tone, update_trigger_alert_emails, update_alert_trigger_pushover, \
    update_alert_trigger_alert_filter
from lib.config_handler import load_config_file
from lib.logging_handler import CustomLogger
from lib.mysql_handler import MySQLDatabase
from lib.redis_handler import RedisCache
from lib.system_handler import get_systems, update_system_general, update_system_email_settings, \
    update_system_pushover_settings, update_system_telegram_settings, update_system_alert_emails, add_system, \
    delete_radio_system, update_system_facebook_settings
from lib.user_handler import authenticate_user
from lib.webhook_handler import update_system_webhooks, update_trigger_webhooks

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
    db.initialize_db()
except Exception as e:
    logger.error(f'Error while <<connecting>> to the <<MySQL Database:>> {e}')
    exit(1)

try:
    rd = RedisCache(config_data)
    logger.info("Redis Pool Connection Pool connected successfully.")
except Exception as e:
    logger.error(f'Error while <<connecting>> to the <<Redis Cache:>> {e}')
    exit(1)

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if not os.getenv('SECRET_KEY'):
    try:
        with open(os.path.join(root_path + '/etc', 'secret_key.txt'), 'rb') as f:
            app.config['SECRET_KEY'] = f.read()
    except FileNotFoundError:
        secret_key = os.urandom(24)
        with open(os.path.join(root_path + '/etc', 'secret_key.txt'), 'wb') as f:
            f.write(secret_key)
            app.config['SECRET_KEY'] = secret_key
else:
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


def clear_loop_manager(system_short_name, action="start"):
    try:
        if action == "start":
            logger.info(f"Starting Clear Loop for {system_short_name}")
            if system_short_name not in stop_signals:
                stop_signals[system_short_name] = Event()
            Thread(target=clear_old_items, args=(system_short_name,), daemon=True).start()
        elif action == "restart":
            logger.info(f"Restarting Clear Loop for {system_short_name}")
            if system_short_name in stop_signals:
                stop_signals[system_short_name].set()
                time.sleep(2)
                del stop_signals[system_short_name]

            if system_short_name not in stop_signals:
                stop_signals[system_short_name] = Event()

            Thread(target=clear_old_items, args=(system_short_name,), daemon=True).start()
        elif action == "stop":
            logger.info(f"Stopping Clear Loop for {system_short_name}")
            if system_short_name in stop_signals:
                stop_signals[system_short_name].set()
                time.sleep(2)
                del stop_signals[system_short_name]
        else:
            logger.error(f"Unknown Loop Management Action {action}")

    except Exception as e:
        logger.error(f"An error occurred in clear_loop_management: {str(e)}")


# Loop to run that clears old detections.
def clear_old_items(system_short_name):
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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticated = session.get('authenticated')

        if not authenticated:
            logger.debug(f"Redirecting User: Current session data: {session.items()}")

            return redirect(url_for('index'))
        else:
            logger.debug(f"User Authorized: Current session data: {session.items()}")

        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if not username or not password:
        flash('Username and Password Required', 'danger')
        return redirect(url_for('index'))

    auth_result = authenticate_user(db, username, password)
    flash(auth_result["message"], 'success' if auth_result["success"] else 'danger')
    return redirect(url_for('admin_index') if auth_result["success"] else url_for('index'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/', methods=['GET'])
def index():
    logger.debug(session)
    return render_template("index.html")


@app.route('/admin', methods=['GET'])
@login_required
def admin_index():
    return render_template("admin_index.html")


@app.route('/admin/systems', methods=['GET'])
@login_required
def admin_edit_system():
    region = config_data.get("general", {}).get("region", "US")
    if region not in ["US", "CA"]:
        region = "US"
    return render_template("edit_systems.html", region=region)


@app.route('/admin/add_system', methods=['GET', 'POST'])
@login_required
def admin_add_system():
    logger.debug(request.form)
    update_result = add_system(db, request.form)
    if update_result.get("success"):
        clear_loop_manager(request.form.get('system_short_name'), action='start')
        flash(f"Added System {request.form.get('system_name')}", 'success')
    else:
        flash(update_result.get("message"), 'danger')
    redirect_url = url_for('admin_edit_system')
    return redirect(redirect_url)


@app.route('/admin/delete_system', methods=['POST'])
@login_required
def admin_delete_system():
    try:
        # Validate incoming JSON data
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        system_id = int(request_dict.get("system_id"))
        system_name = request_dict.get("system_name")
        system_short_name = request_dict.get('system_short_name')

        if system_id is None:
            logger.error("Missing system ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID)."}), 400
        result = delete_radio_system(db, system_id)
        if result.get("success"):
            clear_loop_manager(system_short_name, action="stop")
            logger.debug("System successfully deleted")
            flash(f"System {system_name} successfully deleted.", "success")
            return jsonify({"success": True, "message": f"System {system_name} successfully deleted."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except ValueError as e:
        logger.error(f"Value Error: {e}")
        return jsonify(
            {"success": False, "message": "Invalid data format. System ID must be integer."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_system_general', methods=['POST'])
@login_required
def admin_save_system_general():
    result = {"success": False, "message": "This is a message", "result": []}
    logger.debug(request.form)
    # if update changes short name stop clear thread and start new with new shortname

    update_result = update_system_general(db, request.form)
    if request.form.get("system_short_name").strip().lower() != request.form.get(
            "system_short_name_orig").strip().lower():
        logger.debug("System Name Changed")
        clear_loop_manager(request.form.get(
            "system_short_name_orig"), action="stop")
        clear_loop_manager(request.form.get(
            "system_short_name"), action="start")

    if update_result.get("success"):
        result["success"] = True
        result["message"] = f"Updated General Settings"
    else:
        result["success"] = False
        result["message"] = update_result.get("message")

    return jsonify(result)


@app.route('/admin/save_system_email_settings', methods=['POST'])
@login_required
def admin_save_system_email_settings():
    result = {"success": False, "message": "This is a message", "result": []}
    logger.debug(request.form)
    update_result = update_system_email_settings(db, request.form, config_data)
    if update_result.get("success"):
        result["success"] = True
        result["message"] = f"Updated Email Settings"
    else:
        result["success"] = False
        result["message"] = update_result.get("message")

    return jsonify(result)


@app.route('/admin/save_system_emails', methods=['POST'])
@login_required
def admin_save_system_emails():
    try:
        # Validate incoming JSON data
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        system_id = request_dict.get("system_id")
        system_emails = request_dict.get("system_emails")

        if system_id is None or system_emails is None:
            logger.error("Missing system ID or system emails in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or system emails)."}), 400

        if not isinstance(system_emails, list):
            logger.error("Invalid type for system_emails, expected a list.")
            return jsonify({"success": False, "message": "Invalid data format for emails."}), 400

        # Process the update
        result = update_system_alert_emails(db, system_id, system_emails)
        logger.debug("Emails updated successfully for system ID %s", system_id)
        return jsonify(result)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


@app.route('/admin/save_system_pushover', methods=['POST'])
@login_required
def admin_save_system_pushover():
    result = {"success": False, "message": "This is a message", "result": []}
    logger.debug(request.form)
    update_result = update_system_pushover_settings(db, request.form, config_data)
    if update_result.get("success"):
        result["success"] = True
        result["message"] = f"Updated Pushover Settings"
    else:
        result["success"] = False
        result["message"] = update_result.get("message")

    return jsonify(result)


@app.route('/admin/save_system_facebook', methods=['POST'])
@login_required
def admin_save_system_facebook():
    result = {"success": False, "message": "This is a message", "result": []}
    logger.debug(request.form)
    update_result = update_system_facebook_settings(db, request.form, config_data)
    if update_result.get("success"):
        result["success"] = True
        result["message"] = f"Updated Facebook Settings"
    else:
        result["success"] = False
        result["message"] = update_result.get("message")

    return jsonify(result)


@app.route('/admin/save_system_telegram', methods=['POST'])
@login_required
def admin_save_system_telegram():
    result = {"success": False, "message": "This is a message", "result": []}
    logger.debug(request.form)
    update_result = update_system_telegram_settings(db, request.form, config_data)
    if update_result.get("success"):
        result["success"] = True
        result["message"] = f"Updated Telegram Settings"
    else:
        result["success"] = False
        result["message"] = update_result.get("message")

    return jsonify(result)


@app.route('/admin/save_system_webhooks', methods=['POST'])
@login_required
def admin_save_system_webhooks():
    try:
        # Extract JSON data from request
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        # Validate the presence of system_id and system_webhooks in the request data
        system_id = request_dict.get("system_id")
        system_webhooks = request_dict.get("system_webhooks")

        if system_id is None or system_webhooks is None:
            logger.error("Missing system ID or system webhooks in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or system webhooks)."}), 400

        if not isinstance(system_webhooks, list):
            logger.error("Invalid type for system_webhooks, expected a list.")
            return jsonify({"success": False, "message": "Invalid data format for webhooks."}), 400

        # Update system webhooks using the provided data
        result = update_system_webhooks(db, system_id, system_webhooks)
        return jsonify(result)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


@app.route('/admin/triggers', methods=['GET'])
@login_required
def admin_edit_trigger():
    region = config_data.get("general", {}).get("region", "US")
    if region not in ["US", "CA"]:
        region = "US"
    return render_template("edit_triggers.html", region=region)


@app.route('/admin/add_trigger', methods=['POST'])
@login_required
def admin_add_trigger():
    logger.debug(request.form)
    update_result = add_alert_trigger(db, request.form)
    if update_result.get("success"):
        flash(f"Added Trigger {request.form.get('trigger_name')}", 'success')
    else:
        flash(update_result.get("message"), 'danger')
    redirect_url = url_for('admin_edit_trigger', _external=True) + f"?system_id={request.form.get('system_id')}"
    return redirect(redirect_url)


@app.route('/admin/delete_trigger', methods=['POST'])
@login_required
def admin_delete_trigger():
    try:
        # Validate incoming JSON data
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        system_id = int(request_dict.get("system_id"))
        trigger_id = int(request_dict.get("trigger_id"))
        trigger_name = request_dict.get("trigger_name")

        if system_id is None or trigger_id is None:
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400
        result = delete_alert_trigger(db, system_id, trigger_id)
        if result.get("success"):
            logger.debug("Trigger successfully deleted")
            flash(f"Trigger {trigger_name} successfully deleted.", "success")
            return jsonify({"success": True, "message": f"Trigger {trigger_name} successfully deleted."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except ValueError as e:
        logger.error(f"Value Error: {e}")
        return jsonify(
            {"success": False, "message": "Invalid data format. Trigger ID and System ID must be integers."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_general', methods=['POST'])
@login_required
def admin_save_trigger_general():
    try:
        # Validate incoming JSON data
        form_data = request.form
        logger.debug(form_data)
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('system_id') or not form_data.get('trigger_id'):
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_trigger_general(db, form_data)
        if result.get("success"):
            logger.debug(f"Trigger {form_data.get('trigger_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Trigger {form_data.get('trigger_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_two_tone', methods=['POST'])
@login_required
def admin_save_trigger_two_tone():
    try:
        # Validate incoming JSON data
        form_data = request.form
        logger.debug(form_data)
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('system_id') or not form_data.get('trigger_id'):
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_trigger_two_tone(db, form_data)
        if result.get("success"):
            logger.debug(f"Trigger {form_data.get('trigger_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Trigger {form_data.get('trigger_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_long_tone', methods=['POST'])
@login_required
def admin_save_trigger_long_tone():
    try:
        # Validate incoming JSON data
        form_data = request.form
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('system_id') or not form_data.get('trigger_id'):
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_trigger_long_tone(db, form_data)
        if result.get("success"):
            logger.debug(f"Trigger {form_data.get('trigger_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Trigger {form_data.get('trigger_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_hi_low_tone', methods=['POST'])
@login_required
def admin_save_trigger_hi_low_tone():
    try:
        # Validate incoming JSON data
        form_data = request.form
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('system_id') or not form_data.get('trigger_id'):
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_trigger_hi_low_tone(db, form_data)
        if result.get("success"):
            logger.debug(f"Trigger {form_data.get('trigger_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Trigger {form_data.get('trigger_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_alert_filter', methods=['POST'])
@login_required
def admin_save_trigger_alert_filter():
    try:
        # Validate incoming JSON data
        form_data = request.form
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('system_id') or not form_data.get('trigger_id'):
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_trigger_alert_filter(db, form_data)
        if result.get("success"):
            logger.debug(f"Trigger {form_data.get('trigger_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Trigger {form_data.get('trigger_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_emails', methods=['POST'])
@login_required
def admin_save_trigger_emails():
    try:
        # Validate incoming JSON data
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        trigger_id = request_dict.get("trigger_id")
        system_emails = request_dict.get("trigger_emails")

        if trigger_id is None or system_emails is None:
            logger.error("Missing Trigger ID or trigger emails in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (Trigger ID or trigger emails)."}), 400

        if not isinstance(system_emails, list):
            logger.error("Invalid type for trigger_emails, expected a list.")
            return jsonify({"success": False, "message": "Invalid data format for emails."}), 400

        # Process the update
        result = update_trigger_alert_emails(db, trigger_id, system_emails)
        logger.debug("Emails updated successfully for trigger ID %s", trigger_id)
        return jsonify(result)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


@app.route('/admin/save_trigger_pushover', methods=['POST'])
@login_required
def admin_save_trigger_pushover():
    try:
        # Validate incoming JSON data
        form_data = request.form
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('system_id') or not form_data.get('trigger_id'):
            logger.error("Missing system ID or Trigger ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_trigger_pushover(db, form_data, config_data)
        if result.get("success"):
            logger.debug(f"Trigger {form_data.get('trigger_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Trigger {form_data.get('trigger_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_trigger_webhooks', methods=['POST'])
@login_required
def admin_save_trigger_webhooks():
    try:
        # Extract JSON data from request
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        # Validate the presence of system_id and system_webhooks in the request data
        system_id = request_dict.get("system_id")
        trigger_id = request_dict.get("trigger_id")
        trigger_webhooks = request_dict.get("trigger_webhooks")

        if system_id is None or trigger_webhooks is None or trigger_id is None:
            logger.error("Missing System ID, Trigger ID or system webhooks in the request.")
            return jsonify(
                {"success": False,
                 "message": "Missing necessary information (Trigger ID, System ID or trigger webhooks)."}), 400

        if not isinstance(trigger_webhooks, list):
            logger.error("Invalid type for trigger_webhooks, expected a list.")
            return jsonify({"success": False, "message": "Invalid data format for webhooks."}), 400

        # Update system webhooks using the provided data
        result = update_trigger_webhooks(db, system_id, trigger_webhooks)
        return jsonify(result)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


@app.route('/admin/filters', methods=['GET'])
@login_required
def admin_edit_filter():
    region = config_data.get("general", {}).get("region", "US")
    if region not in ["US", "CA"]:
        region = "US"

    return render_template("edit_alert_filters.html", region=region)


@app.route('/admin/add_filter', methods=['POST'])
@login_required
def admin_add_filter():
    logger.debug(request.form)
    update_result = add_filter(db, request.form)
    if update_result.get("success"):
        flash(f"Added Transcript Filter {request.form.get('alert_filter_name')}", 'success')
    else:
        flash(update_result.get("message"), 'danger')
    redirect_url = url_for('admin_edit_filter')
    return redirect(redirect_url)


@app.route('/admin/delete_filter', methods=['POST'])
@login_required
def admin_delete_filter():
    try:
        # Validate incoming JSON data
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        filter_id = int(request_dict.get("filter_id"))
        filter_name = request_dict.get("filter_name")

        if filter_id is None:
            logger.error("Missing filter id in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (filter ID)."}), 400

        result = delete_filter(db, filter_id)
        if result.get("success"):
            logger.debug("Filter successfully deleted")
            flash(f"Filter {filter_name} successfully deleted.", "success")
            return jsonify({"success": True, "message": f"Filter {filter_name} successfully deleted."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except ValueError as e:
        logger.error(f"Value Error: {e}")
        return jsonify(
            {"success": False, "message": "Invalid data format. Filter ID must be integers."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_filter_general', methods=['POST'])
@login_required
def admin_save_filter_general():
    try:
        # Validate incoming JSON data
        form_data = request.form
        if not form_data:
            logger.error("No Form data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        if not form_data.get('alert_filter_id'):
            logger.error("Missing Filter ID in the request.")
            return jsonify(
                {"success": False, "message": "Missing necessary information (system ID or Trigger ID)."}), 400

        result = update_alert_filter_general(db, form_data)
        if result.get("success"):
            logger.debug(f"Filter {form_data.get('alert_filter_name')} successfully updated.")
            return jsonify(
                {"success": True, "message": f"Filter {form_data.get('alert_filter_name')} successfully updated."}), 200
        else:
            logger.debug(result.get('message'))
            return jsonify({"success": False, "message": result.get("message")}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "Unexpected Error Occurred"}), 400


@app.route('/admin/save_filter_keywords', methods=['POST'])
@login_required
def admin_save_filter_keywords():
    try:
        # Extract JSON data from request
        request_dict = request.get_json()
        if not request_dict:
            logger.error("No JSON data provided.")
            return jsonify({"success": False, "message": "No data provided."}), 400

        # Validate the presence of system_id and system_webhooks in the request data
        alert_filter_id = request_dict.get("alert_filter_id")
        alert_filter_name = request_dict.get("alert_filter_name")
        filter_keywords = request_dict.get("filter_keywords")

        if alert_filter_id is None or filter_keywords is None:
            logger.error("Missing Alert Filter ID or filter keywords in the request.")
            return jsonify(
                {"success": False,
                 "message": "Missing necessary information (Alert Filter ID or filter keywords)."}), 400

        if not isinstance(filter_keywords, list):
            logger.error("Invalid type for filter keywords, expected a list.")
            return jsonify({"success": False, "message": "Invalid data format for filter keywords."}), 400

        # Update system webhooks using the provided data
        result = update_filter_keyword(db, alert_filter_id, alert_filter_name, filter_keywords)
        return jsonify(result)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON.")
        return jsonify({"success": False, "message": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


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
            process_result = process_call_data(db, rd, config_data, system_data.get("result")[0], call_data)
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
@login_required
def api_get_triggers():
    system_id = request.args.get('system_id', None)
    trigger_id = request.args.get('trigger_id', None)

    system_data_result = get_alert_triggers(db, system_id, trigger_id)

    return jsonify(system_data_result)


@app.route("/api/get_systems")
@login_required
def api_get_systems():
    system_id = request.args.get('system_id', None)
    with_triggers = request.args.get('with_triggers', False)

    # Fetch system data once
    system_data_result = get_systems(db, system_id=system_id, with_triggers=with_triggers)

    return jsonify(system_data_result)


@app.route("/api/get_filters")
@login_required
def api_get_filters():
    filter_id = request.args.get('filter_id', None)
    filter_data_result = get_alert_filters(db, alert_filter_id=filter_id)
    return jsonify(filter_data_result)


systems = get_systems(db)
if systems.get("result", []):
    for system in systems.get("result"):
        system_short_name = system.get("system_short_name")
        clear_loop_manager(system_short_name, action="start")

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=8002, debug=False)
