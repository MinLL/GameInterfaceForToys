"""Encoding functionality for communicating with bluetooth device.

Based on the official DG-LAB Coyote specification:
https://github-com.translate.goog/dg-lab-opensource?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=da

Byte encoding functionality ported from previous work by @rezreal (https://github.com/rezreal/coyote)

Licensed under the MIT License, (c) 2022 S. F. S.
"""

import struct


def encode_power(pow_a: int, pow_b: int) -> bytes:
    """
    Encodes e-stim power settings into a three-byte message for consumption by the bluetooth device.

    Valid input range (int): 0 <= pow_[a|b] <= 2047.

    :param pow_a: output strength of channel a
    :param pow_b: output strength of channel b
    :return: three-byte bytes object
    """
    # Dark bit-wise magic courtesy of @rezreal (https://github.com/rezreal/coyote)
    b0 = (pow_a >> 5) & 0b00111111
    b1 = ((pow_a & 0b00011111) << 3) | ((pow_b & 0b11111111111) >> 8)
    b2 = pow_b & 0b11111111
    return bytes([b2, b1, b0])  # flip the first and third bytes


def encode_pattern(ax: int, ay: int, az: int) -> bytes:
    """
    Encodes e-stim pattern state into a three-byte message for consumption by the bluetooth device.

    Valid input range:
        0 <= ax <=   31 pulse length in ms
        0 <= ay <= 1023 pause duration (between pulses) in ms
        0 <= az <=   31 amplitude

        :param ax: pulse duration in ms
        :param ay: pause duration in ms
        :param az: amplitude
        :return: three-byte bytes object

    """

    # Dark bit-wise magic courtesy of @rezreal (https://github.com/rezreal/coyote)
    b0 = ((az & 0b00011110) >> 1)
    b_ = ((az & 0b00000001) << 15) | ((ay & 0b00000011_11111111) << 5 | (ax & 0b00011111))

    # Unpack the unsigned short (Uint16) into two unsigned chars (Uint8).
    b1, b2 = struct.pack("H", b_)

    # Verify split:
    # print(format(b_, "b"), "-->", format(b1, "b"), format(b2, "b"))

    # Identical: # struct.pack("BBB", b2, b1, b0)

    return bytes([b1, b2, b0])  # cut and append first byte behind the third byte (??) # fixme, this makes no sense


def test_function_validity():
    """
    This function verifies that the encoding functions work exactly the same as their original javascript version.

    Only meant for debugging/testing purposes!

    More specifically, fuzzy_power_data.json & fuzzy_pattern_data.json contain samples of input/output pairs created
    with the original javascript encoding functions. This function iterates through the data and verifies that
    the outputs match the inputs.

    fuzzy_power_data.json contains a single json object with the following schema:

    [
        input/output pair,
        input/output pair,
        input/output pair,
        ...
    ]

    With each input/output pair having the following schema:

     [pow_a,pow_b]
          |  [byte message]
          |        |
     [1721,83,[83,200,53],"53 c8 35","1010011 11001000 110101"]  # example
     |-------||---------| |----------------------------------|
        input    output     output in base 16 & base 2 for human convenience

    pow_a & pow_b are integers
    byte message is a list of three integers, each integer representing a single 8-bit unsigned integer byte.


    fuzzy_pattern_data.json follows a similar schema:

    [
        input/output pair,
        input/output pair,
        input/output pair,
        ...
    ]

    With each input/output pair having the following schema:

    [ax, ay, az]
          |   [byte message]
          |         |
    [[8,685,26,[168,85,13],"a8 55 d","10101000 1010101 1101"]  # example
     |--------||---------| |--------------------------------|
        input     output    output in base 16 & base 2 for human convenience

    pow_ax, ay & az are integers
    byte message is a list of three integers, each integer representing a single 8-bit unsigned integer byte.

    """

    import json
    print("Testing power data")
    with open("fuzzy_power_data.json", "r") as infile:
        power_test_data = json.load(infile)

    s0 = power_test_data[0]
    pow_a, pow_b, ba, hex_repr, bit_repr = s0
    out = encode_power(pow_a, pow_b)
    if bytes(ba) == out:  # test for identity
        pass
    else:
        raise Exception(f"Error, {bytes(ba)} does not match {out}")

    for sample in power_test_data:
        pow_a, pow_b, ba, hex_repr, bit_repr = sample
        out = encode_power(pow_a, pow_b)
        if bytes(ba) == out:
            # print(f"{ba[0]}: {out[0]}\n{ba[1]}: {out[1]}\n{ba[2]}: {out[2]}")
            # print("---")
            pass
        else:
            raise Exception(f"Error, {bytes(ba)} does not match {out}")
    print("No errors found!")

    print("Testing pattern data")
    with open("fuzzy_pattern_data.json", "r") as infile:
        pattern_test_data = json.load(infile)

    s0 = pattern_test_data[0]
    ax, ay, az, ba, hex_repr, bit_repr = s0
    out = encode_pattern(ax, ay, az)
    if bytes(ba) == out:  # test for identity
        pass
    else:
        raise Exception(f"Error, {bytes(ba)} does not match {out}")

    for sample in pattern_test_data:
        ax, ay, az, ba, hex_repr, bit_repr = sample
        out = encode_pattern(ax, ay, az)
        if bytes(ba) == out:
            # print(f"{ba[0]}: {out[0]}\n{ba[1]}: {out[1]}\n{ba[2]}: {out[2]}")
            # print("---")
            pass
        else:
            raise Exception(f"Error, {bytes(ba)} does not match {out}")
    print("No errors found!")
