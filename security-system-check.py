import json
import logging
import os
import smtplib
import ssl
import time
from datetime import datetime
import gettext
import requests
from dotenv import load_dotenv
from requests.auth import HTTPDigestAuth

# Try importing RPi.GPIO, but mock it if unavailable
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Path to the file simulating GPIO pin states
    PIN_STATES_FILE = "simulated_pins.json"

    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        PUD_UP = "PUD_UP"

        def setmode(self, mode):
            print(f"GPIO setmode({mode}) simulated")

        def setup(self, pin, mode, pull_up_down=None):
            print(f"GPIO setup(pin={pin}, mode={mode}, pull_up_down={pull_up_down}) simulated")

        def input(self, pin):
            # Read the current state of the pin from the JSON file
            try:
                with open(PIN_STATES_FILE, "r") as f:
                    pin_states = json.load(f)
                # Get the state of the requested pin
                state = pin_states.get(str(pin), False)
                print(f"MockGPIO: input(pin={pin}) called - returning {state}")
                return state
            except FileNotFoundError:
                print(f"MockGPIO: {PIN_STATES_FILE} not found. Simulating all pins as False.")
                return False
            except json.JSONDecodeError:
                print(f"MockGPIO: Failed to decode {PIN_STATES_FILE}. Simulating all pins as False.")
                return False

        def cleanup(self):
            print("GPIO cleanup simulated")


    GPIO = MockGPIO()

# Custom implementation to replace `distutils.util.strtobool`
def to_bool(value):
    value = value.lower()
    if value in {'1', 'true', 'yes', 'y'}:
        return True
    if value in {'0', 'false', 'no', 'n'}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


# load environment
load_dotenv()
USER_HOME = os.getenv('USER_HOME')

# Dynamically construct the file path
cameras_file_path = os.path.join(USER_HOME, 'cameras.json')

# Read camera data from JSON file
with open(cameras_file_path, 'r') as file:
    camera_data = json.load(file)

# Get interior cameras
interior_cameras = [camera['ip'] for camera in camera_data if camera['type'] == 'interior']
exterior_cameras = [camera['ip'] for camera in camera_data if camera['type'] == 'exterior']
all_cameras = [camera['ip'] for camera in camera_data]


el = gettext.translation('base', localedir=os.path.join(USER_HOME,'locales'), languages=[os.environ['LANGUAGE']])
el.install()
_ = el.gettext

# constants
SYSTEM_ARMED_PIN = 16
SYSTEM_ALARM_PIN = 20
LOGFILE_PATH = os.environ['LOGFILE_PATH']
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', filename=LOGFILE_PATH,
                    level=int(os.environ['LOG_DEBUG']))

"""
 Functions used within the main loop of the program.
"""


def privacy_api_calls(camera_ips=None, status=False):
    """
    :param camera_ips: A list of camera IP addresses. Defaults to an empty list.
    :param status: A boolean indicating whether to enable or disable the privacy mask. Defaults to False.
    :return: None
    """
    for ip in camera_ips:
        for i in range(4):
            encode_blend = str(status).lower()  # Convert to 1 or 0 (True/False)
            url = f'http://{ip}/cgi-bin/configManager.cgi?action=setConfig&VideoWidget[0].Covers[{i}].EncodeBlend={encode_blend}'
            response = requests.get(url,
                                    auth=HTTPDigestAuth(os.environ['CAMERA_USERNAME'], os.environ['CAMERA_PASSWORD']))

            if response.status_code != 200:
                logger.error(f"Request to {ip} returned status code {response.status_code}.")


def send_email(subject, body):
    if to_bool(os.getenv('EMAIL_ENABLE', 'False')):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(os.environ['EMAIL_SERVER'], int(os.environ['EMAIL_PORT']), context=context) as server:
            server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASSWORD'])
            server.sendmail(os.environ['FROM_ADDRESS'], os.environ['TO_ADDRESS'], f'Subject: {subject}\n\n{body}')


def log_current_state():
    logger.info(_('System Armed: ') + str(last_armed_state))
    logger.info(_('System Alarm: ') + str(last_alarm_state))


def update_privacy_masks():
    if last_armed_state and not last_alarm_state:
        print("Interior privacy masks off")
        log_current_state()
        logger.info('Interior privacy masks off')
        send_email(subject=_('Interior privacy masks off'), body=_('Privacy change'))
        privacy_api_calls(camera_ips=interior_cameras)
    elif last_alarm_state:
        print("All privacy masks off")
        log_current_state()
        logger.info('All privacy masks off')
        send_email(subject=_('All privacy masks off'), body=_('Privacy change'))
        privacy_api_calls(camera_ips=all_cameras)
    else:
        print("Privacy masks on")
        log_current_state()
        logger.info('Privacy masks on')
        send_email(subject=_('Privacy masks on'), body=_('Privacy change'))
        privacy_api_calls(camera_ips=all_cameras, status=True)


"""
    Main Program
"""
send_email(_('Controller booted'), datetime.now().strftime('%c') + _(': Powered on'))

GPIO.setmode(GPIO.BCM)
GPIO.setup(SYSTEM_ARMED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SYSTEM_ALARM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Get the current state
logger.info('GPIO configured')
last_armed_state = GPIO.input(SYSTEM_ARMED_PIN)
last_alarm_state = GPIO.input(SYSTEM_ALARM_PIN)

# send an initial email and set the initial state for privacy masks
update_privacy_masks()

try:
    while True:
        time.sleep(1)
        current_armed_stated = GPIO.input(SYSTEM_ARMED_PIN)
        current_alarm_stated = GPIO.input(SYSTEM_ALARM_PIN)

        if current_armed_stated != last_armed_state:
            last_armed_state = current_armed_stated
            update_privacy_masks()
        if current_alarm_stated != last_alarm_state:
            last_alarm_state = current_alarm_stated
            update_privacy_masks()

except KeyboardInterrupt:
    GPIO.cleanup()
