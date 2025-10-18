import configparser
import logging
import re
import subprocess
import time
import os

# --- SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.ini')
LOG_FILE = os.path.join(SCRIPT_DIR, 'proximity_lock.log')

def setup_logging(enable_logging):
    if not enable_logging: return
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def read_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
    config.read(CONFIG_FILE)
    settings = config['settings']
    password = settings.get('password') if settings.get('password') != 'your_password_here' else None
    return {
        'mac': settings.get('phone_mac'),
        'lock_cmd': settings.get('lock_command'),
        'interval': settings.getint('poll_interval'),
        'logging': settings.getboolean('enable_logging'),
        'media_control': settings.getboolean('enable_media_control'),
        'password': password
    }

# --- MODIFIED FUNCTION ---
def is_phone_near(mac_address):
    """
    Pings the device and returns True if successful, False otherwise.
    This is more reliable than checking for RSSI text.
    """
    try:
        # We run the command and check its exit code. 0 means success.
        # stdout and stderr are discarded as we don't need to read them.
        result = subprocess.run(
            ["l2ping", "-c", "1", mac_address],
            timeout=5,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            logging.info("Phone found nearby (ping successful).")
            return True
        else:
            logging.info("Phone not found (ping failed).")
            return False
    except (subprocess.TimeoutExpired):
        logging.info("Phone not found (ping timed out).")
        return False
    except FileNotFoundError:
        logging.error("'l2ping' command not found. Is bluez-utils installed?")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

def run_command(command):
    try:
        subprocess.Popen(command.split())
    except Exception as e:
        logging.error(f"Failed to run command '{command}': {e}")

def lock_screen(config):
    logging.info("Device is far. Locking screen.")
    run_command("notify-send 'Proximity Lock' 'Phone out of range. Locking screen.'")
    if config['media_control']:
        logging.info("Pausing media player.")
        run_command("playerctl pause")
    run_command(config['lock_cmd'])

def unlock_screen(config):
    if not config['password']:
        logging.warning("Password not set in config.ini. Cannot unlock.")
        return
    logging.info("Device is near. Unlocking screen.")
    time.sleep(1)
    subprocess.run(["xdotool", "type", config['password']])
    subprocess.run(["xdotool", "key", "Return"])
    if config['media_control']:
        logging.info("Resuming media player.")
        time.sleep(1)
        run_command("playerctl play")

def main():
    try:
        config = read_config()
        setup_logging(config['logging'])
    except Exception as e:
        print(f"FATAL: Could not start script. Error: {e}")
        return

    logging.info("--- Proximity Lock script started ---")
    logging.info(f"Watching for device: {config['mac']}")
    is_locked = False

    while True:
        # --- MODIFIED LOGIC ---
        phone_is_near = is_phone_near(config['mac'])

        if not phone_is_near: # If phone is far
            if not is_locked:
                lock_screen(config)
                is_locked = True
        else: # If phone is near
            if is_locked:
                unlock_screen(config)
                is_locked = False

        time.sleep(config['interval'])

if __name__ == "__main__":
    main()