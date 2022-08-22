"""Load patterns from all JSON files in directory and make them accessible as dictionary."""
import os
import json


def _load_pattern(fname):
    with open(fname, "r") as infile:
        content = json.load(infile)
    return content

def load_patterns(dir_name):
    files = os.listdir(dir_name)
    files = [file for file in files if file.endswith(".json")]
    patterns = {}

    for filename in files:
        content = _load_pattern(filename)
        patterns[filename] = content

    return patterns

if __name__ == "__main__":
    patterns = load_patterns(".")  # Load all patterns in current directory
    print(patterns)

    # Hint: Use patterns[key] as the argument for the signal function in CoyoteInterface:
    # > ci.signal(power=300, patterns=patterns["vibrator_standard1LP.wav"], duration=0, channel="a")

