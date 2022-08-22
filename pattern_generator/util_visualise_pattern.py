"""Function to visualise a dg-lab coyote e-stim pattern of the form [[ax, ay, az], [ax, ay, az] ...] with matplotlib."""

# todo: Needs heavy refactoring to fit more smoothly with create_pattern.py.

import matplotlib.pyplot as plt
import math

# a sort of "sampling rate" for the generated visualisation function. Increase to improve fidelity, decrease to shorten
# computation time.
resolution = 100


def _sine(samples=1000, frequency=1000, amplitude=1.) -> float:
    """Auxiliary function to compute y as a function of x for a sinusoid.

        :param samples: todo. Don't touch the default value, lol.
        :param frequency: todo.
        :param amplitude: Set sine value amplitude.
    """

    return amplitude * math.sin(2 * math.pi * samples / frequency)  # 2 * required for a full cycle


def _create_full_sine_wave(wave_resolution=1000, amplitude=1.) -> tuple:
    """Creates a full cycle sine wave at wave_resolution number of samples.

        :param wave_resolution: Set sampling rate (or "resolution") of sine wave.
        :param amplitude: Set amplitude of sine wave.

        :return: returns a tuple of lists X & Y for easy plotting in matplotlib.

    """

    X = [x for x in range(wave_resolution)]

    return X, [_sine(x, frequency=wave_resolution, amplitude=amplitude) for x in X]


def _map_z_to_sine_amplitude(z: int) -> float:
    """maps/scales 0 <= z <= 31 to the values 0.0 <= a <=1.

        :param z: Amplitude value between 0 and 31.

        :return: Returns a float between 0. and 1.
    """

    _min = 0.
    _max = 1.

    b = _min
    a = (_max - b) / 31

    return z * a + b


def construct_wave(pattern: list) -> tuple[list, list]:
    S_2 = []
    for state in pattern:
        x, y, z = state

        amplitude = _map_z_to_sine_amplitude(z)
        X, Y = _create_full_sine_wave(resolution, amplitude=amplitude)  # Remake sine-wave for every state according to amplitude (az).

        signal = Y * x
        S_2.extend(signal)

        silence = [0] * resolution * y
        S_2.extend(silence)

    return [x / resolution for x in range(len(S_2))], S_2


def visualise_pattern(pattern: list, title: str = "Untitled"):
    """Visualise a dg-lab coyote pattern [[ax, ay, az], [ax, ay, az], ...], where

        0 <= ax <=   31 pulse length in ms
        0 <= ay <= 1023 pause duration (between pulses) in ms
        0 <= az <=   31 amplitude

        :param pattern: This is the pattern list of lists of integers.
        :param title: Optional figure title to pass to matplotlib.
        """
    # construct waveform from pattern data
    X, Y = construct_wave(pattern=pattern)

    # prepare matplotlib graphs
    fig, ax = plt.subplots(nrows=1)

    ax.set_xlabel("milliseconds")
    ax.set_ylabel("amplitude (z)")
    ax.plot(X, Y)

    if title:
        ax.set_title(title)

    # render
    fig.show()


if __name__ == "__main__":
    # test patterns
    patterns = [[[10, 90, 10]],  # simple, one-state pattern of 10 ms pulse, 90 ms pause, amplitude 10

                [[5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 135, 20],
                 [5, 135, 20], [5, 135, 20], [5, 135, 20], [5, 95, 20], [4, 86, 20], [4, 76, 20],
                 [4, 66, 20], [3, 57, 20], [3, 37, 20], [3, 37, 20], [2, 28, 20], [2, 18, 20], [1, 14, 20],
                 [1, 9, 20]],  # varied pattern of 20 states (original)

                [[5, 135, 5],  # varied pattern of 20 states with increasing pulse width and intensity
                 [5, 135, 5],
                 [5, 135, 5],
                 [5, 135, 5],
                 [5, 135, 7],
                 [5, 135, 7],
                 [5, 135, 7],
                 [5, 135, 7],
                 [5, 135, 9],
                 [5, 95, 9],
                 [10, 86, 11],
                 [10, 76, 13],
                 [10, 66, 15],
                 [15, 57, 17],
                 [15, 37, 19],
                 [15, 37, 21],
                 [20, 28, 23],
                 [20, 18, 25],
                 [25, 14, 27],
                 [25, 9, 29]],

                [[20, 0, 30],  # Placeholder pattern with decreasing intensity and increasing pauses between pulses
                 [20, 1, 28],
                 [20, 2, 26],
                 [20, 3, 24],
                 [20, 4, 22],
                 [20, 5, 20],
                 [20, 6, 18],
                 [20, 7, 16],
                 [20, 8, 14],
                 [20, 9, 12],
                 [20, 10, 10],
                 [20, 11, 8],
                 [20, 12, 6],
                 [20, 13, 4],
                 [20, 14, 2],
                 [20, 15, 0]]
                ]

    pattern_single_state, pattern_original, pattern_long, pattern_intense = patterns

    # Visualise a single-state pattern
    visualise_pattern(pattern_single_state, title="single state pattern")

    # Visualise a longer pattern with multiple states
    visualise_pattern(pattern_long, title="multi-state pattern")

    # If you have prepared patterns as JSON files in your current directory, uncomment the following:
    # import util_load_patterns
    # patterns = util_load_patterns.load_patterns(".")
    #
    # for key in patterns.keys():
    #     visualise_pattern(patterns[key], title=key)


