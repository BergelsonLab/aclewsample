import sys
import subprocess as sp
import os
from random import shuffle
from util import FFProbe

def choose_onsets(f, n=5, t=2, start=30):
    """
    Args:
        f (str): audio file
        n (int): number of sections to choose
        t (int): section time in minutes
        start (int): how many minutes into the file to start selecting

    Returns:
        timestamps: list of onset/offset tuples
    """
    metadata = FFProbe(f)
    try:
        length = metadata.streams[0].durationSeconds()
        length_min = int(length) / 60
        min_range = range(start, length_min-t-3)
        shuffled = shuffle(min_range)
        selected = []
        for x in shuffled:
            if len(selected) >= n:
                break
            if not any(_overlap(x, y) for y in selected):
                selected.append(x)
        return [(x-2, x+3) for x in selected]
    except (IndexError):
        print  "{} was a problem file. skipped.".format(f)

def _splice(f, out_dir, timestamps):
    """
    Args:
        f (str): parent audio file
        out_dir (str): directory to dump spliced output
        timestamps (list): list of onset/offset tuples
    """
    for i, x in enumerate(timestamps):
        command = ["ffmpeg",
                "-ss", "{}".format(x[0]),
                "-t", "{}".format(x[1]-x[0]),
                "-i", f,
                "-acodec", "copy",
                    os.path.join(out_dir, "{}_{}_{}-{}.mp3".format(f, i, x[0], x[1]))
                ]
        sp.call(command)

def _overlap(x, y):
    pass

def splice(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".wav") or file.endswith(".mp3"):
                timestamps = choose_onsets(os.path.join(root, file))
                _splice(os.path.join(root, file), output_dir, timestamps)


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]


    # choose_onsets()

