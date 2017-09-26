import sys
import os

import splice
import pympi


def generate_templates(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".mp3") or file.endswith(".wav"):
                timestamps = splice.choose_onsets(os.path.join(root, file))
                timestamps = [(x*60000,y*60000) for x, y in timestamps]
                print timestamps
                eaf = pympi.Eaf()
                eaf.add_tier("code")
                eaf.add_tier("context")
                eaf.remove_tier("default")
                for ts in timestamps:
                    eaf.add_annotation("code", ts[0], ts[1])
                    eaf.add_annotation("context", ts[0]-120000, ts[1]+60000)
                eaf.to_file(os.path.join(output_dir, "{}.eaf".format(file[:-4])))

if __name__ == "__main__":

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    generate_templates(input_dir, output_dir)