import logging
import smtplib
import ssl
import traceback
from datetime import datetime, timezone
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from lib.config_handler import decrypt_password

module_logger = logging.getLogger('icad_alerting_api.email')


class EmailSender:
    """EmailSender is a class responsible for sending emails with given configurations.

        Attributes:
            sender_email (str): Sender's email address.
            sender_name (str): Sender's name.
            smtp_username (str): Username for the SMTP server.
            smtp_password (str): Password for the SMTP server.
            smtp_hostname (str): Hostname of the SMTP server.
            smtp_port (int): Port number of the SMTP server.
            smtp_security (str): Security protocol for the SMTP server, either SSL or TLS.
        """

    def __init__(self, global_config_data, system_config_data):
        """Initializes the EmailSender with configuration data.

                Args:
                    global_config_data (dict): A dictionary containing global configuration data.
                    system_config_data (dict): A dictionary containing system configuration data.
        """

        self.sender_email = system_config_data["email_address_from"]
        self.sender_name = system_config_data["email_text_from"]
        self.smtp_username = system_config_data["smtp_username"]
        self.smtp_password = decrypt_password(system_config_data["smtp_password"], global_config_data)
        self.smtp_hostname = system_config_data["smtp_hostname"]
        self.smtp_port = system_config_data["smtp_port"]

    def send_email(self, to, subject, body_html):
        """Sends an alert email with the given parameters.

                Args:
                    to (list): A list of recipient email addresses.
                    subject (str): The subject of the email.
                    body_html (str): The HTML body of the email.

                Returns:
                    None
        """
        module_logger.info("Sending Alert Email")

        # Validate the recipient list
        if not isinstance(to, list) or not to:
            error_message = "Invalid recipient list"
            return {"success": False, "message": error_message}

        # Create a multipart message object
        message = MIMEMultipart()
        message['From'] = formataddr(
            (str(Header(self.sender_name, 'utf-8')),
             self.sender_email))

        # Extract the domain from the sender's email address
        sender_domain = self.sender_email.split('@')[1]

        # Determine whether to use 'To' or 'Bcc' field for the recipient addresses based on list size
        if len(to) == 1:
            message['To'] = to[0]
        else:
            message['To'] = f'Undisclosed Recipients <noreply@{sender_domain}>'
            message['Bcc'] = ", ".join(to)

        # Set the subject of the email
        message['Subject'] = subject

        # Attach the HTML message body
        html_part = MIMEText(body_html, 'html')
        message.attach(html_part)

        try:
            # Connect to the SMTP server and send the email based on the chosen security protocol deciphered from
            # port number
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_hostname, self.smtp_port,
                                      context=ssl.create_default_context()) as smtp_server:
                    smtp_server.login(self.smtp_username, self.smtp_password)
                    smtp_server.send_message(message)
                    return {"success": True, "message": "Email sent successfully using SSL"}

            elif self.smtp_port == 587:
                with smtplib.SMTP(self.smtp_hostname, self.smtp_port) as smtp_server:
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login(self.smtp_username, self.smtp_password)
                    smtp_server.send_message(message)
                    return {"success": True, "message": "Email sent successfully using TLS"}

            else:
                error_message = f'Unsupported security protocol: {self.smtp_port}'
                return {"success": False, "message": error_message}

        except smtplib.SMTPAuthenticationError as e:
            error_message = f"SMTP authentication occurred: {e}"
            return {"success": False, "message": error_message}

        except smtplib.SMTPException as e:
            error_message = f"SMTP error occurred: {e}"
            return {"success": False, "message": error_message}

        except Exception as e:
            error_message = f"An error occurred: {e}"
            return {"success": False, "message": error_message}


def generate_system_alert_email(global_config_data, system_config_data, alert_data, call_data):
    """
    Generates the subject and body of an alert email by replacing placeholders with actual data.

    :param system_config_data: Dictionary containing system configuration data
    :param alert_data: Dictionary containing data about the trigger alert
    :param call_data: Dictionary containing data about the call
    :return: Tuple containing the subject and body of the email
    """
    test_mode = global_config_data.get("general", {}).get("test_mode", True)

    stream_url = system_config_data.get("stream_url") or ""

    email_subject = system_config_data.get("email_alert_subject", "Dispatch Alert")
    email_body = system_config_data.get("email_alert_body",
                                        '{trigger_list} Alerted at {timestamp}<br><br>{transcript}<br><br><a href="{audio_wav_url}">Click for Alert Audio</a><br><br><a href="{stream_url}">Click for Audio Stream</a>')

    # Convert the epoch timestamp to a datetime object
    current_time_dt = datetime.fromtimestamp(call_data.get("start_time", 0), tz=timezone.utc).astimezone()

    # Format the datetime object to a human-readable string with the timezone
    current_time = current_time_dt.strftime('"%H:%M %b %d %Y" %Z')

    if test_mode:
        email_body = f"<font color=\"red\"><b>TEST TEST TEST TEST</b></font><br><br>{email_body}<br><br>"

    trigger_list = ", ".join([triggered_alert.get("trigger_name") for triggered_alert in alert_data])

    try:
        mapping = {
            "trigger_list": trigger_list,
            "timestamp": current_time,
            "timestamp_epoch": call_data.get("start_time"),
            "transcript": call_data.get("transcript", {}).get("transcript", "No Transcript"),
            "audio_wav_url": call_data.get("audio_wav_url", ""),
            "audio_m4a_url": call_data.get("audio_m4a_url", ""),
            "stream_url": stream_url
        }

        # Format the email subject and body using the mapping
        email_subject = email_subject.format_map(mapping)
        email_body = email_body.format_map(mapping)

        return email_subject, email_body

    except Exception as e:
        module_logger.exception(f"Failed to generate trigger alert email: {e}")
        return None, None


def generate_trigger_alert_email(global_config_data, system_config_data, trigger_data, alert_data, call_data):
    """
    Generates the subject and body of an alert email by replacing placeholders with actual data.

    :param system_config_data: Dictionary containing system configuration data
    :param alert_data: Dictionary containing data about the trigger alert
    :param call_data: Dictionary containing data about the call
    :return: Tuple containing the subject and body of the email
    """
    test_mode = global_config_data.get("general", {}).get("test_mode", True)

    stream_url = trigger_data.get("stream_url") or ""
    if not stream_url:
        stream_url = system_config_data.get("stream_url") or ""

    email_subject = system_config_data.get("email_alert_subject", "Dispatch Alert - {trigger_name}")
    email_body = system_config_data.get("email_alert_body",
                                        '{trigger_list} Alerted at {timestamp}<br><br>{transcript}<br><br><a href="{audio_wav_url}">Click for Alert Audio</a><br><br><a href="{stream_url}">Click for Audio Stream</a>')

    # Convert the epoch timestamp to a datetime object
    current_time_dt = datetime.fromtimestamp(call_data.get("start_time", 0), tz=timezone.utc).astimezone()

    # Format the datetime object to a human-readable string with the timezone
    current_time = current_time_dt.strftime('"%H:%M %b %d %Y" %Z')

    if test_mode:
        email_body = f"<font color=\"red\"><b>TEST TEST TEST TEST</b></font><br><br>{email_body}<br><br>"

    trigger_list = ", ".join([triggered_alert.get("trigger_name") for triggered_alert in alert_data])
    try:
        mapping = {
            "trigger_list": trigger_list,
            "timestamp": current_time,
            "timestamp_epoch": call_data.get("start_time"),
            "transcript": call_data.get("transcript", {}).get("transcript", "No Transcript"),
            "audio_wav_url": call_data.get("audio_wav_url", ""),
            "audio_m4a_url": call_data.get("audio_m4a_url", ""),
            "stream_url": stream_url
        }

        # Format the email subject and body using the mapping
        email_subject = email_subject.format_map(mapping)
        email_body = email_body.format_map(mapping)

        return email_subject, email_body

    except Exception as e:
        module_logger.exception(f"Failed to generate trigger alert email: {e}")
        return None, None

