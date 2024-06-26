import logging
import time

import bcrypt
from flask import session

module_logger = logging.getLogger('icad_alerting_api.user_handler')


def get_users(db, user_id=None, username=None, limit_one=False):
    base_query = """
SELECT
    ur.*,
    us.*
    FROM users ur
    LEFT JOIN user_security us on ur.user_id = us.user_id
    """

    where_clauses = []
    parameters = []
    if user_id is not None:
        where_clauses.append("ur.user_id = %s")
        parameters.append(user_id)
    if username is not None:
        where_clauses.append("ur.user_username = %s")
        parameters.append(username)

    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)
        final_query = f"{base_query} {where_clause} GROUP BY ur.user_id"
    else:
        final_query = f"{base_query} GROUP BY ur.user_id"

    users_result = db.execute_query(final_query, tuple(parameters) if parameters else None, fetch_mode="one" if limit_one else "many")
    module_logger.debug(f"users_result: {users_result}")
    return users_result


def password_validate(database_password, given_password):
    return bcrypt.checkpw(given_password.encode('utf-8'), database_password.encode('utf-8'))


def authenticate_user(db, username, password):
    user_result = get_users(db, username=username, limit_one=True)
    if not user_result['success']:
        return {"success": False, "message": user_result['message']}

    if not user_result['result']:
        return {"success": False, "message": "User not found."}

    user_data = user_result['result']
    if not password_validate(user_data.get("user_password"), password):
        set_invalid_result = set_login_values(db, user_data, True)
        if not set_invalid_result:
            module_logger.error("Can not set database values for failed login attempt.")
        module_logger.warning(f"Password Incorrect: {username}")
        return {"success": False, "message": "Invalid Username or Password"}

    # update database with login values and reset lockout values
    set_valid_result = set_login_values(db, user_data)
    if not set_valid_result:
        module_logger.error("Can not set database values for logged in user")
        return {"success": False, "message": "Internal Error"}

    # set session keys
    set_session = set_session_keys(user_data)
    if not set_session:
        module_logger.error("Can not set session values for logged in user")
        return {"success": False, "message": "Internal Error"}

    # passed all check return true user is logged in.
    return {"success": True, "message": "Authenticated Successfully"}


def set_login_values(db, user_data, is_failed=False):
    if not is_failed:
        module_logger.debug(f'Adding Success Values {user_data["user_username"]}')
        # Set Values for newly logged in User
        user_success_query = 'UPDATE user_security SET last_login_date = %s, failed_login_attempts = 0, account_locked_until = 0 WHERE user_id = %s'
        user_success_params = (int(time.time()), user_data["user_id"])
        user_success_result = db.execute_commit(user_success_query, user_success_params)
        if user_success_result["success"]:
            return True
        else:
            return False
    else:
        # Set Values for failed user.
        if user_data["failed_login_attempts"] > 5:
            module_logger.debug(f'Locking Account {user_data["user_username"]}')
            # too many failures lock account
            user_fail_lockout_query = 'UPDATE user_security SET account_locked_until = %s WHERE user_id = %s'
            user_fail_lockout_params = (int(time.time()) + 900, user_data["user_id"],)
            user_fail_lockout_result = db.execute_commit(user_fail_lockout_query, user_fail_lockout_params)
            if user_fail_lockout_result["success"]:
                return True
            else:
                return False
        else:
            # increase failures
            module_logger.debug(f'Increasing failed login values {user_data["user_username"]}')
            user_fail_query = 'UPDATE user_security SET failed_login_attempts = %s WHERE user_id = %s'
            user_fail_params = (user_data["failed_login_attempts"] + 1, user_data["user_id"])
            user_fail_result = db.execute_commit(user_fail_query, user_fail_params)
            if user_fail_result["success"]:
                return True
            else:
                return False


def set_session_keys(user_data):
    module_logger.debug(user_data)
    module_logger.debug(f"Setting Session Keys")

    try:
        username = user_data.get('user_username')

        if not username:
            raise ValueError("No Username")

        session['username'] = username
        session['authenticated'] = True

        return True
    except IndexError as e:
        module_logger.error(f"IndexError: {e}", exc_info=True)
        return False
    except AttributeError as e:
        module_logger.error(f"AttributeError: {e}", exc_info=True)
        return False
    except KeyError as e:
        module_logger.error(f"KeyError: {e}", exc_info=True)
        return False
    except Exception as e:  # Catch any other exceptions that might be raised
        module_logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return False


def update_user_password(db, username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_up_pass_query = f'UPDATE users SET user_password = %s WHERE user_username = %s'
    user_up_pass_params = (hashed_password, username)
    user_up_pass_result = db.execute_commit(user_up_pass_query, user_up_pass_params)
    return user_up_pass_result


def user_change_password(db, username, current_password, new_password):
    user_result = get_users(db, username=username, limit_one=True)
    if not user_result['success']:
        return {"success": False, "message": user_result['message']}

    if not user_result['result']:
        return {"success": False, "message": "Username or Password incorrect"}

    user_data = user_result['result']
    if not password_validate(user_data.get("user_password"), current_password):
        module_logger.warning(f"Password Incorrect: {username}")
        return {"success": False, "message": "Invalid Username or Password"}

    user_up_pass_result = update_user_password(db, username, new_password)

    if user_up_pass_result["success"]:
        return {"success": True, "message": "Password Changed Successfully"}
    else:
        return {"success": False, "message": f"Password Change Failed. {user_up_pass_result.get('message')}"}
