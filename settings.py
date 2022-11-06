from common.constants import *
## Edit the following variables to configure this script

# Important variables to configure for all users:
LOG_PATH = '../Documents/My Games/Skyrim VR/Logs/Script/Papyrus.0.log' # Full path to the Papyrus log that the script should parse
# LOG_PATH = '../Documents/My Games/Fallout4/Logs/Script/Papyrus.0.log' # Full path to the Papyrus log that the script should parse
CHARACTER_NAME = "Min"  # The name of your character. 

# Toy configuration
TOY_TYPE = [TOY_LOVENSE]
DD_VIB_MULT = 2  # Duration of vibration event is multiplied by this value. 
WARN_ON_STACK_DUMP = True  # Loop short vibrations to notify user of Stack Dumps. Set to False to disable.
BUTTPLUG_STRENGTH_MAX = 100 # Set to a value between 1 - 100 to cap the strength at a % of your toy's maximum

# Configuration if using Chaster:
CHASTER_TOKEN = ""

LOCK_NAME = "Self-lock"  # The name of the lock to manipulate. Must be unique.
# LOCK_NAME = "Keyholder lock"  # The name of the lock to manipulate. Must be unique.
# Chaster + Sexlab Defeat Configuration
CHASTER_DEFEAT_MIN = 60 * 60 * 12  # Minimum number of hours to add on party defeat
CHASTER_DEFEAT_MAX = CHASTER_DEFEAT_MIN * 2  # Maximum number of hours to add on party defeat
LOVENSE_HOST = "127.0.0.1"
# LOVENSE_HOST = "192.168.0.195"

# Configuration if using DG-Lab Coyote:
COYOTE_UID = "C1:A9:D8:0C:CB:1D"  # Set to the Bluetooth UID for your particular Coyote device
COYOTE_MULTIPLIER = 7.68  # Multiplier to translate between 0-100 vibration intensity and e-stim intensity.
COYOTE_DEFAULT_CHANNEL = "a"  # Set default output channel. Accepts "a" or "b"
COYOTE_SAFE_MODE = True  # Enable or disable safe mode. This caps the max e-stim output of the device. Warning: Don't touch unless you know what you're doing!
