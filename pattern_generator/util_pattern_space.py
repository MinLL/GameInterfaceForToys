"""
util_pattern_space.create_space() creates a linear sequence (or "space") of [x, y, z] values ranging from least to most
intensive. create_pattern.py maps from WAV file amplitude to this space: Low amplitude corresponds to low (e-stim)
intensity, high amplitude corresponds to high (e-stim) intensity.

Feel free to experiment with the default values for create_space(), or create your own solution space.

y_lower_bound/y_upper_bound set limits for the y values. The higher the range for y, the longer between pulses, i.e.
less intensive.
The lower the y value range, the shorter duration between pulses, i.e. more intensive.

Analogously, a lower x range correspond to more sharply felt sensations (due to fewer pulses firing in a row), while
a higher x range corresponds to less sharply felt sensation (due to more pulses in a row).

note: You can easily invert the relationship between x and y by setting x_lower_bound to a higher value than
x_upper_bound!

See how your changes take effect with
> python create_pattern.py -v [filename.wav]
"""


# todo: Test, test, test!
def create_space(y_lower_bound=9, y_upper_bound=20, x_lower_bound=10, x_upper_bound=1):
    space = []

    for i in range(0, 31 + 1):  # corresponds neatly to the 0-31 value boundaries for x and z.
        x = x_upper_bound - round((((x_upper_bound - x_lower_bound) / 31) * i))
        y = y_upper_bound - round((((y_upper_bound - y_lower_bound) / 31) * i))
        z = i  # z == 0 equals no signal. Here, z just steps up linearly from 0 to 31.
        space.append((x, y, z))
    return space


def _xy_to_frequency(x: int, y: int) -> int:
    frequency = y + x
    return frequency


def _conforms_to_ratio(x: int, y: int) -> bool:  # 1:9 == 10% : 90 % x/y ratio.
    return all([x / (x + y) <= 0.10, y / (x + y) >= 0.90])


def _frequency_to_xy(frequency: int):
    x = ((frequency / 1000) ** 0.5) * 15
    x = round(x)  # round to int
    y = frequency - x
    return x, y


# This alternative space attempts to satisfy criteria from the official DG-LAB Coyote specification.
# deprecated; doesn't work (=feel) that well.
def create_space_alt():
    space = [_frequency_to_xy(i) for i in range(10, 1000 + 1)]

    # strip out combinations that violate the 1:9 ratio.
    space = [pair for pair in space if _conforms_to_ratio(pair[0], pair[1])]

    # Since x is capped at 15, let's map the z variable to x * 2.
    # Thereby intensity scales linearly with x. Should work:
    space = [(tup[0], tup[1], tup[0] * 2) for tup in space]

    return space


if __name__ == "__main__":
    solution_space = create_space()
    print("Available linear solution space [[x, y, z], [x, y, z] ...]: ")
    print(solution_space)