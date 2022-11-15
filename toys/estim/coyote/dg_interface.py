"""
The following makes available for integration into SkyrimToyInterface by "Min"
(https://www.loverslab.com/files/file/22380-skyrim-irl-toy-chastity-interface-le-se-ae-vr/) a class which interfaces
directly with the DG-Lab Coyote e-stim box over bluetooth.

Note: This code requires the bluetooth package "bleak" (https://pypi.org/project/bleak/) to be installed from pypi.
It is recommended that you use python's built-in package manager "pip":


>> pip install bleak


Code written based on the official DG-LAB Coyote specification:
https://github-com.translate.goog/dg-lab-opensource?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=da

Byte encoding functionality ported from previous work by @rezreal (https://github.com/rezreal/coyote)


Disclaimer:

USE THIS SOFTWARE AT YOUR OWN RISK. THE COMPATIBLE E-STIM DEVICE IS VERY POWERFUL, MEANING THAT HARDWARE MALFUNCTIONS
OR UNDETECTED SOFTWARE BUGS MAY LEAD TO SUDDEN AND/OR VERY PAINFUL ELECTRICAL STIMULATION. THERE IS NO GUARANTEE OF
IT BEING 100 % RELIABLE AND SAFE ON YOUR COMPUTER SYSTEM OR PLATFORM. CONSEQUENTLY, THE AUTHOR(S) ASSUME NO LIABILITY
OF ANY KIND.

TAKE SPECIAL CARE NOT TO SET THE E-STIM POWER TO AN ORDER OF MAGNITUDE HIGHER THAN YOU WANTED; ALL IT TAKES IS A SINGLE
TYPO. THE SAFE MODE IS THERE FOR A REASON.

REMEMBER: SUDDEN, UNEXPECTED ELECTRICAL STIMULATION IS FELT MUCH MORE STRONGLY THAN CONTINUOUS STIMULATION.


PLEASE USE COMMON SENSE AND USE E-STIM RESPONSIBLY.

DO NOT MOVE OR OTHERWISE INTERACT WITH THE ELECTRODES WHILE THE E-STIM DEVICE IS ACTIVE. YOU MIGHT ACCIDENTALLY
PROVIDE AN UNINTENDED PATH FOR THE CURRENT TO GO THROUGH VULNERABLE BODY PARTS.

DO NOT USE E-STIM ABOVE THE WAIST, ESPECIALLY NOT ACROSS THE CHEST.

DO NOT USE E-STIM WHILE IN AN ALTERED STATE OF MIND. BEING EXCITED LIKE A LUSTY ARGONIAN MAID IS OKAY, THOUGH.

DO NOT USE E-STIM ON A PARTNER WITHOUT THEIR EXPRESS CONSENT. TAKE EXTRA CARE WHEN PLAYING WITH A PARTNER.


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Licensed under the MIT License, (c) 2022 S. F. S.
"""

import bleak  # bluetooth functionality
import toys.estim.coyote.dg_encoding as dg_encoding  # custom functionality for encoding communication to the bluetooth device
import logging
import time
import asyncio
from toys.base import FEATURE_ESTIM
from toys.estim.estim import Estim
import random
from common.util import *

class CoyoteInterface(Estim):
    """
    DG-LAB Coyote interface for SkyrimToyInterface integration.

    Attributes:
        device_uid (str): The Unique Identifier of the bluetooth e-stim device, usually a string of six base 16 values
                            joined by colons, for example: "D7:ED:72:AF:D7:18".
        power_multiplier (float): Regulates how powerful the e-stim scales compared to "vibration strength". Higher
                            values means stronger stimulation. Be careful!
        default_channel (str): Set default output channel, either "a" or "b".
        safe_mode (bool): Caps e-stim device power output to max 37.5 % of total capacity. Don't turn off unless you know
                            what you are doing! See self._set_pwm() for implementation details.
    """

    def __init__(self, device_uid="C1:A9:D8:0C:CB:1D", power_multiplier=7.68, default_channel="a", safe_mode=True):
        """
        The constructor for the CoyoteInterface class.

        :param device_uid:
        :param power_multiplier:
        :param safe_mode:
        """
        super().__init__("coyote")
        # Set bluetooth device uid and device reference
        self.device_uid = device_uid
        self.device = bleak.BleakClient(self.device_uid)

        # Bluetooth characteristic placeholders; populated in self.connect()
        self._battery_level = None  # battery level
        self._config = None  # configuration
        self._pwm_ab2 = None  # power
        self._pwm_a34 = None  # channel b
        self._pwm_b34 = None  # channel a

        # Caution: the channels a & b are actually switched compared to the official spec, so that a34 outputs to
        # channel b, and b34 to channel a. This is corrected automatically if the following flag is set.
        self.channels_switched = True

        # Set default output channel. This provides the default channel for self.vibrate().
        # You can override the default output channel with self.signal()
        self.default_channel = default_channel

        # Multiplier to map 0-600 to the range accepted by the e-stim box, required for self.vibrate() compatibility.
        #
        # Theoretically, one could translate the range 0-600 vibration strength to the e-stim box's entire 0-2047
        # intensity range. In practice, however, I doubt most people are comfortable with intensities above 1024!
        # This multiplier has a conservative default value, but can be easily changed by the user on instantiation with
        # ci = CoyoteInterface(... power_multiplier = <your value here>, ...).
        # todo: What is the range of possible "vibration strength" values from from SKI? 0-100? 0-300? 0-600?
        # This multiplier assumes a max vibration strength of 600, as per SkyrimToyInterface-alpha3.py
        # 600 max vibration strength * 1.28 power multiplier == 37 % max e-stim intensity (768 out of 2047).
        self.power_multiplier = power_multiplier

        # Flag to indicate connection status
        # fixme: Use self.device.is_connected instead?
        self.is_connected = False

        # Flag: Cap power intensity to 900 out of 2047 (roughly 44 %) for safety reasons. The limit is enforced in
        # the self._set_pwm() method.
        # Do not disable you're unless absolutely certain that you know what you are doing!
        self.safe_mode = safe_mode

        # todo: import patterns from patterns.json and choose according to type of in-game event
        # Placeholder e-stim patterns
        #
        # Pattern schema is a list of lists [[x, y, z], [x, y, z], ...], where
        #
        # x pulse length: 0-31 ms
        # y pause length: 0-1023 ms
        # z amplitude: 0-31
        #
        # See https://github-com.translate.goog/dg-lab-opensource?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=da
        # for more information
        # self.patterns = [
        
        # ]

    #
    # Internal methods
    #

    def _get_pwm(self) -> (int, int):  # return pow_a, pow_b
        """
        Return tuple of current power level of channel a and channel b.
        :rtype: (int, int)
        """
        # todo
        raise NotImplementedError()

    async def _set_pwm(self, pow_a: int, pow_b: int):
        """
        Set power level of channel a and channel b

        Valid input range (int): 0 <= pow_[a|b] <= 2047

        :param pow_a: Output power of channel a
        :param pow_b: Output power of channel b
        """
        # "self.safe_mode == True" limits the amount of e-stim intensity to 37.5 % (768/2047).
        if self.safe_mode:
            in_valid_range = 0 <= pow_a <= 768 and 0 <= pow_b <= 768
        else:
            in_valid_range = 0 <= pow_a <= 2047 and 0 <= pow_b <= 2047

        if in_valid_range:
            # Encode inputs to byte sequence
            message = dg_encoding.encode_power(pow_a, pow_b)

            # Communicate byte sequence to device
            await self.device.write_gatt_char(self._pwm_ab2.uuid, message)
            # Read & confirm new values
            output = await self.device.read_gatt_char(self._pwm_ab2)
            logging.info(f"Wrote byte sequence to _pwm_ab2: {message}, confirmation: {output}")
        else:
            if self.safe_mode:
                logging.error("Caution, safe mode is enabled.")
                logging.error(f"Input values pow_a ({pow_a}) & pow_b ({pow_b}) must both be within the range 0-768!")
            else:
                logging.error(f"Input values pow_a ({pow_a}) & pow_b ({pow_b}) must both be within the range 0-2047!")

    def _calculate_pattern_duration(self, pattern: list) -> int:
        """
        Calculates total duration of a pattern's combined pulses and pauses. Output duration is in milliseconds.

        :param pattern: List of lists of the schema [[ax, ay, az], [ax, ay, az], ...] representing an e-stim pattern.
        :return: Total duration of pattern duration in milliseconds.
        """
        return sum([x[0] + x[1] for x in pattern])

    def _truncate_pattern(self, duration: int, pattern: list) -> list:
        """
        Shorten pattern if it is too long for a given duration.

        :param duration: Intended duration (ms) as given as parameter to vibrate function.
        :param pattern: Pattern which is longer than duration (ms).
        :return: A shortened pattern which is not longer than duration.
        """
        # todo
        raise NotImplementedError

    def _debug(self, strength: int = 256, duration: int = 10, step: int = 1):
        """
        Debug/testing function, please disregard.
        """
        # ramp up power slowly to detect weird discontinuities
        for i in range(strength, 1995, step):
            print(i)
            self.vibrate(duration, i)

    #
    # User-facing functions
    #

    async def connect(self, retries: int = 10):
        """
        Connect to the device and register characteristics.

        :param retries: Indicates the number of attempts to connect before raising an exception and halting the program.
        """

        print("Connecting to device: {} ...".format(self.device_uid))

        saved_exception = ConnectionError
        if not self.device.is_connected:
            for _ in range(retries):
                # Catch time-out errors while we retry
                try:
                    self.is_connected = await self.device.connect()
                    print("Connected!")
                    break
                except (asyncio.TimeoutError, asyncio.CancelledError, bleak.exc.BleakError) as e:
                    # Overwrite generic ConnectionError with actual exception
                    saved_exception = e
                    logging.error(f"Caught TimeoutError or CancelledError exception. Retrying... {e}")
                    self.is_connected = False

        if not self.device.is_connected:
            # raise ConnectionError("Failed to connect to bluetooth device")
            logging.error("Failed to connect to bluetooth device.")
            raise saved_exception

        # Get services
        # Obs: the following can also be accessed without functions through
        # device.services.services (list)
        # device.services.characteristics (list)

        logging.info("Getting services...")
        services = await self.device.get_services()
        services = [service for service in services]  # convert from async iterator to list

        # Pick out and save services and characteristics according to Service UUID
        for service in services:
            if service.uuid == "955a180a-0fe2-f5aa-a094-84b8d4f3e8ad":
                battery_level_service = service
                # logging.info("found battery service: ", service.uuid)

                for characteristic in battery_level_service.characteristics:
                    if characteristic.uuid == "955a1500-0fe2-f5aa-a094-84b8d4f3e8ad":
                        self._battery_level = characteristic
                        # logging.info("found battery level characteristic: ", characteristic.uuid)

            if service.uuid == "955a180b-0fe2-f5aa-a094-84b8d4f3e8ad":
                pwm = service
                # logging.info("found power strength service: ", service.uuid)

                for characteristic in pwm.characteristics:
                    if characteristic.uuid == "955a1504-0fe2-f5aa-a094-84b8d4f3e8ad":
                        # logging.info("found channels strength characteristic: ", characteristic.uuid)
                        self._pwm_ab2 = characteristic

                    if characteristic.uuid == "955a1505-0fe2-f5aa-a094-84b8d4f3e8ad":

                        # logging.info("found channel A characteristic: ", characteristic.uuid)

                        # Caution: xxxx1505/PWM_A34 actually maps to channel b. Switch automatically if
                        # self.channels_switched flag is set to True.
                        if self.channels_switched:
                            self._pwm_b34 = characteristic
                        else:
                            self._pwm_a34 = characteristic

                    if characteristic.uuid == "955a1506-0fe2-f5aa-a094-84b8d4f3e8ad":

                        # logging.info("found channel B characteristic: ", characteristic.uuid)

                        # Caution: xxxx1506/PWM_B34 actually maps to channel a. Switch automatically if
                        # self.channels_switched flag is set to True.
                        if self.channels_switched:
                            self._pwm_a34 = characteristic
                        else:
                            self._pwm_b34 = characteristic

                    if characteristic.uuid == "955a1507-0fe2-f5aa-a094-84b8d4f3e8ad":
                        # logging.info("found config characteristic: ", characteristic.uuid)
                        self._config = characteristic

        # Test connectivity
        # Read the unit power level (%)
        logging.info("Querying battery level...")
        battery_level = await self.device.read_gatt_char(self._battery_level.uuid)

        # Convert from bytearray to hex to decimal
        battery_level_dec = int(battery_level.hex(), 16)
        print("Current device battery level: ", battery_level_dec)

        # write output power = 0 to device
        logging.info("Attempting to communicate command 'set channels strength to 0' to device...")
        message = bytes([0, 0, 0])
        logging.info(f"Writing {message} to {self._pwm_ab2.uuid}")

        # Communicate message to device
        output = await self.device.write_gatt_char(self._pwm_ab2.uuid, message)

        # Read output power from device
        logging.info(f"Reading current strength value from {self._pwm_ab2.uuid}")
        output = await self.device.read_gatt_char(self._pwm_ab2)

        if output == message:
            logging.info("Read: channels strength == {}".format(output))
            print("Device read/write functionality confirmed.\nReady!")
        else:
            logging.error("Device read/write functionality could not be confirmed.")

    async def shutdown(self):
        await self.disconnect()
        
    async def disconnect(self):
        """Disconnect device."""

        print("Disconnecting...")
        self.stop_signal = True
        self.is_connected = False
        output = await self.device.disconnect()

        if not self.device.is_connected:
            print("Disconnected!")

    async def signal(self, power: int, pattern: list, duration: int, channel: str = "a"):
        """
        Send to device an e-stim pattern on channel a or b at a given power for a given duration.

        :param power: Set e-stim power (0 <= x <= 2047)
        :param pattern: Set pattern [ [ax, ay, az], [ax, ay, az], ...]
        :param duration: Set duration in milliseconds.
        :param channel: Set output channel a|b.
        """
        # todo: Enable multi-channel output, i.e. different patterns/power/durations on channels a & b simultaneously.

        # Set channel target (a/b)
        characteristic = self._pwm_b34 if channel == "b" else self._pwm_a34

        # Set killswitch
        self.stop_signal = False
        
        # Set power
        await self._set_pwm(power, power)  # todo: independent power strength for each individual channel. Perhaps thru
        # self.get_pwm()?

        # if we assume that the given duration is in milliseconds (?), then we must calculate how many times the
        # pattern can be executed within that time-frame, depending on the length of the pattern, so that the pattern
        # does not run far longer than the intended duration.
        #
        # If the pattern is way longer than the given duration, just run the pattern once. I don't know whether this
        # will be a big issue, to be honest.

        pattern_duration = self._calculate_pattern_duration(pattern)

        repeats = duration // pattern_duration  # Identical to math.floor(duration / pattern_duration)
        last_power_check = int(time.time())

        # Iterate over the pattern and send each value (ax, ay, az) to the device in succession
        if not repeats:  # run pattern once only
            for state in pattern:
                if self.stop_signal:
                    return
                now = int(time.time())
                # Check to see if power output has been reduced to zero once per second
                if now - last_power_check > 1:
                    if not await self.is_running():
                        return
                    last_power_check = int(time.time())                
                # unpack pattern values
                ax, ay, az = state

                # Determine duration of state (ms)
                time_delta = ax + ay  # consists of sum of pulse duration and pause duration

                # Encode pattern
                message = dg_encoding.encode_pattern(ax, ay, az)

                # Send message to bluetooth device
                output = await self.device.write_gatt_char(characteristic, message)

                # Sleep to avoid spamming the device and causing "frame tearing."
                # fixme: Might work worse than a flat time.sleep(0.1)?
                time.sleep(time_delta / 1000)  # Convert from milliseconds to seconds
        else:
            for _ in range(repeats):  # repeat pattern a number of times
                for state in pattern:
                    if self.stop_signal:
                        return
                    now = int(time.time())
                    # Check to see if power output has been reduced to zero once per second
                    if now - last_power_check > 1:
                        if not await self.is_running():
                            return
                        last_power_check = int(time.time())

                    # unpack pattern values
                    ax, ay, az = state

                    # Determine duration of state (ms)
                    time_delta = ax + ay  # consists of sum of pulse duration and pause duration

                    # Encode pattern
                    message = dg_encoding.encode_pattern(ax, ay, az)

                    # Send message to bluetooth device
                    output = await self.device.write_gatt_char(characteristic, message)

                    # Sleep to avoid spamming the device and causing "frame tearing."
                    #fixme: Might work worse than a flat time.sleep(0.1)?
                    time.sleep(time_delta / 1000)  # Convert from milliseconds to seconds

    async def is_running(self):
        if not self.is_connected: # Process is shutting down.
            return False        
        try:
            output = await self.device.read_gatt_char(self._pwm_ab2)
            pass
        except Exception as e:
            print(e)
            print("Reconnecting...")
            await self.connect()
            return False
        # If power is 0, stop() has been called outside this function.
        if output == bytearray(b'\x00\x00\x00'):
            return False
        return True
    
    def convert_power_vibrate(self, strength: int):
        min_power = 320
        max_power = 768
        vibrateRange = (100 - 0)  
        stimRange = (max_power - min_power)
        # cast float to integer for compatibility with func.
        return int((((strength - 0) * stimRange) / vibrateRange) + min_power)

    async def shock(self, duration: int, strength: int, pattern=""):  #
        """
        Method for compatibility with SkyrimToyInterface. Send a "vibration" signal of given duration and strength.

        :param duration: Vibration duration in milliseconds (ms).
        :param strength: Vibration strength (0 <= x <= 100).
        :param pattern: The pattern to shock with.
        """
        # Vibration already in progress
        if await self.is_running():
            await self.stop()
            timeout = 0
            while await self.is_running() and timeout < 30:
                await asyncio.sleep(0.1)
                timeout += 1
        if not pattern in self.patterns:
            fail("Pattern {} not found - Using default")
            pattern = ""
        pattern = random.choice(self.patterns[pattern])
        await self.signal(power=self.convert_power_vibrate(strength),
                          pattern=pattern,  # todo: Different patterns corresponding to in-game events.
                          duration=(duration * 1000),
                          channel=self.default_channel)
        # Set power back to zero after event is done.
        await self.stop()

    async def stop(self):
        """
        Set power to zero. Caution: This doesn't interrupt patterns already in progress.

        todo: Interrupt-based stop command.
        """
        self.stop_signal = True
        await self._set_pwm(0, 0)

    async def check_in(self):
        return await self.is_running()


if __name__ == "__main__":
    """Execute this file directly to test functionality without SkyrimToyInterface/game integration."""

    # enable INFO level of logging
    logging.basicConfig(level=logging.INFO)

    ci = CoyoteInterface(device_uid="C1:A9:D8:0C:CB:1D",  # These arguments are identical to the class defaults and
                         power_multiplier=1.28,           # are for demonstration only.
                         safe_mode=True)

    # connect to device
    ci.connect(retries=10)
    # # uncomment the following to enable e-stim testing without integration into SKI/TES:V.
    # # USE AT YOUR OWN RISK. USE RESPONSIBLY. SEE DISCLAIMER ABOVE.

    # # Stimulate five seconds (5000 ms) at 200 vibration strength * 1.28 == 12.5 % e-stim intensity
    # # e-stim intensity is calculated based on the power_multiplier, like so:
    # # vibration strength * power_multiplier == 200 * 1.28 == 256 (out of 2047) == 12.5 % e-stim intensity
    # ci.vibrate(5000, 200)
    #
    # # sleep five seconds
    # time.sleep(5)
    #
    # # Stimulate five seconds at 300 vibration strength * 1.28 == 18.75 % e-stim intensity.
    # # 300 * 1.28 == 384 (out of 2047) == 18.75 % e-stim intensity.
    # ci.vibrate(5000, 300)
    #
    # # sleep five seconds
    # time.sleep(5)
    #
    #
    # # You can also provide more detailed e-stim commands directly.
    # # Here we stimulate six seconds at 341 (out of 2047) == 16 % e-stim intensity.
    # # Note that the "power" argument corresponds directly to the e-stim device's internal 0-2047 range and is NOT
    # # translated like in ci.vibrate().
    # # Max allowed e-stim intensity is capped at 37.5 % (768 out of 2047) when the ci.safe_mode flag is set.
    # #
    # ci.signal(power=341,
    #           pattern=[
    #                 [1, 9, 10],
    #                 [2, 8, 10],
    #                 [3, 7, 10],
    #                 [4, 6, 10],
    #                 [5, 5, 10],
    #                 [6, 4, 10],
    #                 [7, 3, 10],
    #                 [8, 2, 10],
    #                 [9, 1, 10],
    #                 [1, 0, 10]],
    #           duration=6000,
    #           channel="a")
    #
    # # Currently just two placeholder patterns are available, but you can add your own:
    # print(ci.patterns)
    #
    # # sleep five seconds
    # time.sleep(5)
    #
    # # finally, this removes the power intensity safeguard (be very careful with ci.vibrate() & ci.signal()
    # # from now on!):
    # ci.safe_mode = False
    #
    # ci.stop()
    # ci.disconnect()
