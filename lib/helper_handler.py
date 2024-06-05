import json
import logging
from datetime import datetime, timezone

module_logger = logging.getLogger("icad_alerting_api.text_handler")


def generate_mapped_content(template, alert_data, call_data, stream_url,
                            test_mode):
    """
    Generates content by replacing placeholders with actual data.

    :param template: Template string with placeholders
    :param alert_data: Dictionary containing data about the alert
    :param call_data: Dictionary containing data about the call
    :param stream_url: Stream URL to be used in the content
    :param test_mode: Flag indicating if the system is in test mode
    :return: Mapped content
    """

    # Convert the epoch timestamp to a datetime object
    current_time_dt = datetime.fromtimestamp(call_data.get("start_time", 0), tz=timezone.utc).astimezone()
    # Format the datetime object to a human-readable string with the timezone
    current_time = current_time_dt.strftime('"%H:%M %b %d %Y" %Z')

    trigger_list = ", ".join([triggered_alert.get("trigger_name") for triggered_alert in alert_data])

    tone_report = generate_tone_data_report(alert_data)

    mapping = {
        "trigger_list": trigger_list,
        "timestamp": current_time,
        "timestamp_epoch": call_data.get("start_time"),
        "transcript": call_data.get("transcript", {}).get("transcript", "No Transcript"),
        "audio_wav_url": call_data.get("audio_wav_url", ""),
        "audio_m4a_url": call_data.get("audio_m4a_url", ""),
        "stream_url": stream_url,
        "tone_report_html": generate_tone_data_report(alert_data, "html"),
        "tone_report_text": generate_tone_data_report(alert_data, "text"),
        "tone_report_json": alert_data,
    }

    if test_mode:
        template = f"TEST TEST TEST TEST\n{template}\nTEST TEST TEST TEST"

    try:
        mapped_content = template.format_map(mapping)
        return mapped_content
    except Exception as e:
        module_logger.exception(f"Failed to generate mapped content: {e}")
        return None


def generate_mapped_json(template, alert_data, call_data, stream_url, test_mode):
    """
    Generates JSON content by replacing placeholders with actual data.

    :param template: Template JSON string or dictionary with placeholders
    :param alert_data: Dictionary containing data about the alert
    :param call_data: Dictionary containing data about the call
    :param stream_url: Stream URL to be used in the content
    :param test_mode: Flag indicating if the system is in test mode
    :return: Mapped JSON string or dictionary
    """

    # Convert the epoch timestamp to a datetime object
    current_time_dt = datetime.fromtimestamp(call_data.get("start_time", 0), tz=timezone.utc).astimezone()

    # Format the datetime object to a human-readable string with the timezone
    current_time = current_time_dt.strftime('"%H:%M %b %d %Y" %Z')

    trigger_list = ", ".join([triggered_alert.get("trigger_name") for triggered_alert in alert_data])

    mapping = {
        "trigger_list": trigger_list,
        "timestamp": current_time,
        "timestamp_epoch": call_data.get("start_time"),
        "transcript": call_data.get("transcript", {}).get("transcript", "No Transcript"),
        "audio_wav_url": call_data.get("audio_wav_url", ""),
        "audio_m4a_url": call_data.get("audio_m4a_url", ""),
        "stream_url": stream_url,
        "tone_report_html": generate_tone_data_report(alert_data, "html"),
        "tone_report_text": generate_tone_data_report(alert_data, "text"),
        "tone_report_json": alert_data,
        "is_test": test_mode
    }

    try:
        # Check if the template is a string (JSON) or a dictionary
        if isinstance(template, str):
            # Load the template JSON string
            json_data = json.loads(template)
        elif isinstance(template, dict):
            json_data = template
        else:
            raise ValueError("Template must be a JSON string or a dictionary")

        # Recursively replace placeholders in the JSON data
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(i) for i in obj]
            elif isinstance(obj, str):
                return obj.format_map(mapping)
            else:
                return obj

        mapped_json_data = replace_placeholders(json_data)

        # Convert back to JSON string if the input was a string
        if isinstance(template, str):
            return json.dumps(mapped_json_data)
        else:
            return mapped_json_data

    except Exception as e:
        module_logger.exception(f"Failed to generate mapped JSON content: {e}")
        return None


def generate_tone_data_report(tone_data_list, report_format='html'):
    """
    Generates a readable report of tone data after processing.

    :param tone_data_list: List of dictionaries containing tone data
    :param report_format: Format of the report ('html' or 'text')
    :return: String report of tone data in the specified format
    """
    report = ""

    for tone_data in tone_data_list:
        trigger_name = tone_data.get('trigger_name', 'Unknown Trigger')

        if report_format == 'html':
            report += f"<strong>Trigger Name: {trigger_name}</strong><br><br>"
        else:
            report += f"**Trigger Name: {trigger_name}**\n\n"

        # Process two_tone
        if tone_data.get('two_tone'):
            if report_format == 'html':
                report += "<strong>Two-Tone Detections:</strong><br>"
            else:
                report += "**Two-Tone Detections:**\n"

            for idx, tone in enumerate(tone_data['two_tone'], 1):
                if report_format == 'html':
                    report += f"{idx}. Tone ID: {tone['tone_id']}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Detected Tones: {tone['detected'][0]}, {tone['detected'][1]}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Tone A Length: {tone['tone_a_length']} seconds<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Tone B Length: {tone['tone_b_length']} seconds<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Start Time: {tone['start']} seconds<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- End Time: {tone['end']} seconds<br><br>"
                else:
                    report += f"{idx}. Tone ID: {tone['tone_id']}\n"
                    report += f"   - Detected Tones: {tone['detected'][0]}, {tone['detected'][1]}\n"
                    report += f"   - Tone A Length: {tone['tone_a_length']} seconds\n"
                    report += f"   - Tone B Length: {tone['tone_b_length']} seconds\n"
                    report += f"   - Start Time: {tone['start']} seconds\n"
                    report += f"   - End Time: {tone['end']} seconds\n\n"

        # Process long_tone
        if tone_data.get('long_tone'):
            if report_format == 'html':
                report += "<strong>Long Tones:</strong><br>"
            else:
                report += "**Long Tones:**\n"

            for idx, tone in enumerate(tone_data['long_tone'], 1):
                if report_format == 'html':
                    report += f"{idx}. Detected Tone: {tone['detected']}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Length: {tone['length']} seconds<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Start Time: {tone['start']} seconds<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- End Time: {tone['end']} seconds<br><br>"
                else:
                    report += f"{idx}. Detected Tone: {tone['detected']}\n"
                    report += f"   - Length: {tone['length']} seconds\n"
                    report += f"   - Start Time: {tone['start']} seconds\n"
                    report += f"   - End Time: {tone['end']} seconds\n\n"

        # Process hi_low_tone
        if tone_data.get('hi_low_tone'):
            if report_format == 'html':
                report += "<strong>Hi-Low Tones:</strong><br>"
            else:
                report += "**Hi-Low Tones:**\n"

            for idx, tone in enumerate(tone_data['hi_low_tone'], 1):
                if report_format == 'html':
                    report += f"{idx}. Detected Tones: {', '.join(map(str, [tone['detected'][0], tone['detected'][1]]))}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Alternations: {tone['alternations']}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Start Time: {tone['start']} seconds<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- End Time: {tone['end']} seconds<br><br>"
                else:
                    report += f"{idx}. Detected Tones: {', '.join(map(str, [tone['detected'][0], tone['detected'][1]]))}\n"
                    report += f"   - Alternations: {tone['alternations']}\n"
                    report += f"   - Start Time: {tone['start']} seconds\n"
                    report += f"   - End Time: {tone['end']} seconds\n\n"

        # Process alert_filter
        if tone_data.get('alert_filter'):
            if report_format == 'html':
                report += "<strong>Alert Filters:</strong><br>"
            else:
                report += "**Alert Filters:**\n"

            for idx, filter_match in enumerate(tone_data['alert_filter'], 1):
                if report_format == 'html':
                    report += f"{idx}. Filter ID: {filter_match['filter_id']}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Filter Name: {filter_match['filter_name']}<br>"
                    report += f"&nbsp;&nbsp;&nbsp;- Matched Text: {filter_match['matched_text']}<br>"
                else:
                    report += f"{idx}. Filter ID: {filter_match['filter_id']}\n"
                    report += f"   - Filter Name: {filter_match['filter_name']}\n"
                    report += f"   - Matched Text: {filter_match['matched_text']}\n"

    return report
