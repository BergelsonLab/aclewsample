import sys
import subprocess as sp
from util import FFProbe

def choose_onsets(f, n=5, t=2):
    """
    Args:
        f (str): audio file
        n (int): number of sections to choose
        t (int): section time in minutes

    Returns:
        timestamps: list of onset/offset tuples
    """
    timestamps = []
    metadata = FFProbe(f)
    try:
        length = metadata.streams[0].durationSeconds()
    except (IndexError):
        print os.path.join(root, file) + " was a problem file. skipped."
    minutes = int(seconds) / 60


def splice(f, out_dir, timestamps):
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
                    os.path.join(out_dir, "{}-{}.mp3".format(i, speaker))
                ]
        sp.call(command)


if __name__ == "__main__":
    sample_csv = sys.argv[1]
    audio_folder = sys.argv[2]
    output = sys.argv[3]


    choose_onsets()

