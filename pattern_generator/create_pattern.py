"""Command line utility to translate wave files to DG-LAB Coyote patterns.

Remember to install the required python packages (tqdm, matplotlib, click):
> pip install -r requirements.txt

"""

# fixme: Spaghetti code ahead.
# todo: refactoring

import json
import wave
import sys
import matplotlib.pyplot as plt
import os
import statistics
# import numpy as np
from tqdm import tqdm  # progress bar support
import click  # command line interface

import util_visualise_pattern


# todo: refactor these utility functions
def _resolution_to_duration(resolution: int, nframes: int, framerate: int, sample_width: int) -> int:
    length = (nframes / framerate) / ((nframes / sample_width) / (framerate / sample_width)) / resolution * 1000
    return int(length)


def _duration_to_resolution(length: int, nframes: int, framerate: int, sample_width: int) -> int:
    resolution = (nframes / framerate) / ((nframes / sample_width) / (framerate / sample_width)) / length * 1000
    return int(resolution)


def _convert_X_to_seconds(X, framerate: int, sample_width: int):
    return [x / (framerate / sample_width) for x in tqdm(X, desc="Scaling x")]


# def _compute_baseline_frequency(data: list, framerate: int):
#     # # totally stolen from SO:
#     # # https://stackoverflow.com/questions/3694918/how-to-extract-frequency-associated-with-fft-values-in-python
#
#     w = np.fft.fft(data)
#     freqs = np.fft.fftfreq(len(w))
#
#     # print(freqs.min(), freqs.max())
#
#     # # Find the peak in the coefficients
#     idx = np.argmax(np.abs(w))
#     freq = freqs[idx]
#     freq_in_hertz = abs(freq * framerate)
#
#     return freq_in_hertz

def _xy_to_frequency(x: int, y: int) -> int:
    frequency = y + x
    return frequency


@click.command()
@click.argument("fname", nargs=-1)
@click.option('--visualise/--no-visualise', "-v", default=False, help='Output accompanying matplotlib figure.')
def main(fname, visualise=False):
    """Command line utility to convert audio (WAV files) into DG-LAB Coyote e-stim patterns. Outputs a JSON file to the directory by default.

    \b
    Remember to install the necessary requirements (tqdm, matplotlib, click):
    > python -m pip install -r requirements.txt

    Usage:

    \b
    # export vibrator_standard1LP.wav as DG-LAB Coyote compatible pattern in JSON format:
    > python create_pattern.py vibrator_standard1LP.wav
    \b
    # The utility accepts multiple WAV files ...
    > python create_pattern.py vibrator_standard1LP.wav vibrator_weak1LP.wav
    \b
    # ... and wildcards:
    > python create_pattern.py *.wav
    \b
    # Use the -v flag to output accompanying matplotlib figures for debugging & reviewing purposes:
    > python create_pattern.py -v vibrator_standard1LP.wav
    \b
    # Show help:
    > python create_pattern.py --help
    """

    if isinstance(fname, tuple):
        if not fname:
            raise FileNotFoundError("Pass at least one filename to the program.")
        for f in fname:
            create_pattern(f, visualise=visualise)
    else:  # one filename was passed; treat as string.
        create_pattern(fname, visualise=visualise)


def create_pattern(fname, visualise=False):
    """Create DG-LAB Coyote pattern based on input wave file and output in the same directory as JSON file.
    Call with visualise=True to output an additional PNG file with matplotlib figure for debugging & review purposes."""

    print(f"filename: {fname}")
    obj = wave.open(fname, "rb")
    framerate, channels, nframes, sample_width = (obj.getframerate(),
                                                  obj.getnchannels(),
                                                  obj.getnframes(),
                                                  obj.getsampwidth()
                                                  )
    duration = nframes / framerate
    duration_rounded = round(nframes / framerate, 2)
    print(f"framerate: {framerate}")
    print(f"channels: {channels}")
    print(f"nframes: {nframes}")
    print(f"file sample width: {sample_width}")
    print(f"length: {duration_rounded} seconds")

    # obj.getparams()
    obj.rewind()

    frames = []
    for _ in range(int(nframes / sample_width)):
        frame = obj.readframes(sample_width)
        frames.append(frame)

    frames_int = [int.from_bytes(t, byteorder=sys.byteorder, signed=True)
                  for t in frames]

    frames_abs = [abs(x) for x in frames_int]

    # Set resolution as a function of sample duration in ms. Higher values for duration equal fewer samples.
    resolution = _duration_to_resolution(100, nframes=nframes, framerate=framerate, sample_width=sample_width)

    # sliding window size
    window = int((framerate / sample_width) / resolution)

    print(f"window: {window}")

    indices = [x for x in range(0, len(frames_abs), window)]

    avg = []
    local_maxima = []

    for i in tqdm(indices, desc="Computing moving average"):
        mean = statistics.mean(frames_abs[i:window + i])
        avg.extend([mean] * window)

        maximum = max(frames_abs[i:window + i])
        local_maxima.extend([maximum] * window)

    # pad to fit Y length, if needed.
    diff = len(frames_abs) - len(avg)
    if diff == 0:
        pass
    elif diff > 0:
        last_value = avg[-1]
        avg.extend([last_value] * diff)
    elif diff < 0:
        # truncate to Y length
        avg = avg[:len(frames_abs)]

    # pad to fit Y length, if needed.
    diff = len(frames_abs) - len(local_maxima)
    if diff == 0:
        pass
    elif diff > 0:
        last_value = local_maxima[-1]
        local_maxima.extend([last_value] * diff)
    elif diff < 0:
        # truncate to Y length
        local_maxima = local_maxima[:len(frames_abs)]

    X = len(frames_abs)
    X = [x for x in range(X)]

    print(f"X length: {len(X)}")
    print(f"number of avg samples: {len(indices)}")
    print(f"state changes/samples pr. second (avg samples/seconds): {len(indices) / (nframes / framerate)}")
    print(
        f"duration in milliseconds pr. avg sample (seconds/avg samples): {(nframes / framerate) / len(indices) * 1000}")

    min_avg = min(avg)
    avg_normalised = [i - min_avg for i in tqdm(avg, desc="Normalising values")]

    # This imported function creates a linear space of [x, y, z] values from least intensive to most intensive.
    # The rest of this function maps from wave amplitude to this linear space of values.
    # Changes to the possible [x, y, z] space are made in the util_pattern_space.py file.
    import util_pattern_space
    space = util_pattern_space.create_space()

    num_of_bins = len(space)  # This should correspond to available amount of combinations.
    bin_size = int(max(avg_normalised) / num_of_bins)
    bin_pegs = [i * bin_size for i in range(0, num_of_bins)]  # off by one: last peg is implicit, open-ended.
    reverse_bin_pegs = bin_pegs[::-1]

    # sort samples into bins and create pattern by mapping to "space". This variable will hold the final pattern.
    pattern = []

    # Create corresponding frequency list
    frequency_list = []

    for i in tqdm(indices, desc="mapping amplitudes to linear pattern space"):
        for j, _bin in enumerate(reverse_bin_pegs):
            if avg_normalised[i] >= _bin:
                x, y, z = space[num_of_bins - 1 - j]
                pattern.append((x, y, z))
                frequency_list.append(_xy_to_frequency(x, y))
                break

    print("Computed pattern: ")
    print("-----")
    print(pattern)
    print("-----")

    if visualise:
        # Output matplotlib figure.
        print("Rendering graph")

        # set font size
        plt.rcParams['font.size'] = 4

        # empty list for baseline frequency
        # frequency_list_alt = []

        # for i in tqdm(indices, desc="computing baseline frequencies"):
        #     data = frames_int[i:window + i]
        #     frequency_list_alt.append(_compute_baseline_frequency(data, framerate=framerate))

        # legend location
        legend_location = "upper right"

        def _X_to_sec(X):  # shorthand for converting x frames to seconds for matplotlib.
            return _convert_X_to_seconds(X, framerate=framerate, sample_width=sample_width)

        sec_X, sec_indices = _X_to_sec(X), _X_to_sec(indices)

        fig, ax = plt.subplots(nrows=6, sharex="all")

        # Plot the wave file normally
        ax[0].plot(sec_X, frames_int)
        ax[0].set_title(fname)
        ax[0].set_ylabel("amplitude")

        # Plot the wave file in absolute terms
        # with moving average
        # with moving maximum
        ax[1].plot(sec_X, frames_abs)
        ax[1].plot(sec_X, avg, color="orange", label="moving average")
        ax[1].plot(sec_X, local_maxima, color="red", label="moving maximum")
        # ax[1].set_ylabel("amplitude (absolute)")
        ax[1].legend(loc=legend_location)

        # plot baseline frequency
        # ax[2].plot(_X_to_sec(indices),
        #            frequency_list_alt,
        #            label="frequency from FFT",
        #            color="grey")
        # ax[2].legend(loc=legend_location)
        # ax[2].set_ylabel("Hz")

        # ax[3].plot(_X_to_sec(indices), frequency_list, label="pseudo-frequency from amplitude", color="grey")
        # ax[3].legend(loc=legend_location)

        # Plot digitised representation in [ax, ay, az] format
        ax[2].step(sec_indices,
                   [item[0] for item in pattern],
                   where="post",
                   label="ax (pulse duration)",
                   color="blue")
        ax[2].legend(loc=legend_location)
        ax[2].set_ylabel("milliseconds")
        ax[2].set_ylim([0, 31])

        ax[3].step(sec_indices,
                   [item[1] for item in pattern],
                   where="post",
                   label="ay (pause duration)",
                   color="orange")
        ax[3].legend(loc=legend_location)
        ax[3].set_ylabel("milliseconds")

        ax[4].step(sec_indices,
                   [item[2] for item in pattern],
                   where="post",
                   label="az (intensity)",
                   color="purple")
        ax[4].legend(loc=legend_location)
        ax[4].set_ylim([0, 31])

        # Plot reconstructed WAV from pattern representation
        wav_X, wav_Y = util_visualise_pattern.construct_wave(pattern=pattern)

        # Scale wav_X to fit with other graphs:
        scale_factor = max(sec_X) / max(wav_X)
        wav_X = [x * scale_factor for x in wav_X]

        ax[5].plot(wav_X, wav_Y, label="Reconstructed wave from pattern")
        ax[5].set_ylabel("amplitude (z)")
        ax[5].set_xlabel("seconds")
        ax[5].legend(loc=legend_location)

        # save figure to PNG file
        viz_fname = os.path.splitext(fname)[0] + ".png"
        plt.savefig(fname=viz_fname, format="png", dpi=1000)
        print(f"Saved figure to {viz_fname}")

    # save pattern to JSON file
    json_fname = os.path.splitext(fname)[0] + ".json"
    with open(json_fname, "w") as outfile:
        json.dump(pattern, outfile)
    print(f"exported pattern to {json_fname}")

    print("\n")


if __name__ == "__main__":
    # used for click command line functionality.
    main()

    # Debugging, please disregard.
    # create_pattern("vibrator_standard1LP.wav", visualise=True)
