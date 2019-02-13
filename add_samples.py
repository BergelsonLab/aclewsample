import sys
import os
from random import shuffle

import pympi
import pandas as pd



def process(file, aclew_data, t=5, start=30, n=5):
    global selected
    length = int(float(aclew_data.length_of_recording))


    eaf = pympi.Eaf(file)
    existing = [(x / 60000, y / 60000)
                for x, y, _ in
                eaf.get_annotation_data_for_tier('context')]

    minute_range = range(start, length - t)
    shuffle(minute_range)
    i = 0
    for x in minute_range:
        if i == n:
            break
        if not overlaps(x, existing, t):
            existing.append((x, x + 5))
            i += 1

    rand_ints = list(range(6, 6 + n))
    shuffle(rand_ints)

    for x in zip(existing[-n:], rand_ints):
        ts = ((x[0][0] + 2) * 60000), ((x[0][1] - 1) * 60000)
        eaf.add_annotation("code", ts[0], ts[1])
        eaf.add_annotation("code_num", ts[0], ts[1], value=str(x[1]))
        eaf.add_annotation(
            "on_off", ts[0], ts[1], value="{}_{}".format(ts[0], ts[1]))
        eaf.add_annotation("context", ts[0] - 120000, ts[1] + 60000)
        eaf.add_tier("notes")
        selected = selected.append({'aclew_id': aclew_data.aclew_id,
                                    'corpus': aclew_data.corpus,
                                    'clip_num': x[1],
                                    'onset': ts[0],
                                    'offset': ts[1]},
                                   ignore_index=True)
        eaf.to_file(os.path.join(output_dir, os.path.basename(file)))






def overlaps(onset, existing, t):
    # print
    if any(overlap(onset, existing_onset, t) for existing_onset, _ in existing):
        return True
    return False


def overlap(x, y, t):
    if y <= x < y + t:
        return True
    elif y - t <= x < y:
        return True
    return False


if __name__ == "__main__":

    start_dir = sys.argv[1]
    output_dir = sys.argv[2]
    aclew_df = pd.read_csv(sys.argv[3])

    selected = pd.DataFrame(
        columns=['aclew_id', 'corpus', 'clip_num', 'onset', 'offset'], dtype=int)

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".eaf"):
                aclew_data = aclew_df.query(
                    'aclew_id == {}'.format(file[:5])).iloc[0]
                process(os.path.join(root, file), aclew_data)

    selected.to_csv('selected_regions.csv', index=False)