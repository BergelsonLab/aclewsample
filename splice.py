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
        minute_range = range(start, length_min-t)
        shuffle(minute_range)
        selected = []
        for x in minute_range:
            if len(selected) >= n:
                break
            if not any(_overlap(x, y, t) for y in selected):
                selected.append(x)
        return [(x, x+2) for x in selected]
    except (IndexError):
        print  "{} was a problem file. skipped.".format(f)

def _splice(f, out_dir, timestamps):
    """
    Args:
        f (str): parent audio file
        out_dir (str): directory to dump spliced output
        timestamps (list): list of onset/offset tuples
    """
    spliced_outputs = []
    for i, x in enumerate(timestamps):
        fname = os.path.join(out_dir, "{}_{}_{}-{}.wav".format(os.path.basename(f)[:-4], i+1, x[0], x[1]))
        command = ["ffmpeg",
                "-ss", "{}".format(x[0]*60),
                "-i", f,
                "-t", "{}".format(x[1] * 60 - x[0] * 60),
                "-acodec", "copy", fname]
        spliced_outputs.append(fname)
        sp.call(command)
    concat_out = os.path.join(out_dir, "{}_concat_all.wav".format(os.path.basename(f)[:-4]))
    # concat_cmd = [
    #     "ffmpeg",
    #     "-i", "\"concat:{}\"".format("|".join(spliced_outputs)),
    #     "-c", "copy", concat_out
    # ]

    concat_cmd = "ffmpeg -i \"concat:{}\" -c copy {}".format("|".join(spliced_outputs), concat_out, shell=True)
    print concat_cmd
    sp.call(concat_cmd)

def _overlap(x, y, t):
    if y < x < y+t:
        return True
    elif y-t < x < y:
        return True
    return False


def splice(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".wav") or file.endswith(".mp3"):
                timestamps = choose_onsets(os.path.join(root, file))
                _splice(os.path.join(root, file), output_dir, timestamps)


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    splice(input_dir, output_dir)

