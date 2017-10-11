import sys
import os
import shutil

import splice
import pympi
import pandas as pd

basic_00_07 = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_00-07mo.etf'
basic_08_18 = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_08-18mo.etf'
basic_19_36 = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_19-36mo.etf'
basic_00_07_pfsx = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_00-07mo.pfsx'
basic_08_18_pfsx = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_08-18mo.pfsx'
basic_19_36_pfsx = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_19-36mo.pfsx'

casillas_00_07 = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_00-07mo.etf'
casillas_08_18 = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_08-18mo.etf'
casillas_19_36 = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_19-36mo.etf'
casillas_00_07_pfsx = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_00-07mo.pfsx'
casillas_08_18_pfsx = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_08-18mo.pfsx'
casillas_19_36_pfsx = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_19-36mo.pfsx'

conicet_00_07 = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_00-07mo.etf'
conicet_08_18 = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_08-18mo.etf'
conicet_19_36 = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_19-36mo.etf'
conicet_00_07_pfsx = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_00-07mo.pfsx'
conicet_08_18_pfsx = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_08-18mo.pfsx'
conicet_19_36_pfsx = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_19-36mo.pfsx'


def choose_template(info):
    age = info.age_mo_round
    corpus = info.corpus
    if 0 <= age <= 7:
        if corpus == "Conicet Argentina":
            return conicet_00_07, conicet_00_07_pfsx
        elif corpus == "Casillas":
            return casillas_00_07, casillas_00_07_pfsx
        else:
            return basic_00_07, basic_00_07_pfsx
    elif 8 <= age <= 18:
        if corpus == "Conicet Argentina":
            return conicet_08_18, conicet_08_18_pfsx
        elif corpus == "Casillas":
            return casillas_08_18, casillas_08_18_pfsx
        else:
            return basic_08_18, basic_08_18_pfsx
    elif 19 <= age <= 36:
        if corpus == "Conicet Argentina":
            return conicet_19_36, conicet_19_36_pfsx
        elif corpus == "Casillas":
            return casillas_19_36, casillas_19_36_pfsx
        else:
            return basic_19_36, basic_19_36_pfsx



def generate_templates(sample, output_dir):
    selected = pd.DataFrame(columns = ['aclew_id', 'corpus', 'clip_num', 'onset', 'offset'], dtype=int)

    for corpus, group in sample.groupby('corpus'):
        os.makedirs(os.path.join(output_dir, corpus))
        for i, record in group.iterrows():
            timestamps = splice.choose_onsets(int(record.length_of_recording))
            timestamps = [(x * 60000, y * 60000) for x, y in timestamps]
            timestamps.sort(key=lambda tup: tup[0])
            aclew_id = record.aclew_id
            try:
                etf_path, pfsx_path = choose_template(record)
            except:
                print
            print timestamps
            eaf = pympi.Eaf(etf_path)
            eaf.add_tier("code")
            eaf.add_tier("context")
            eaf.add_tier("code_num")
            eaf.add_tier("on_off")
            for i, ts in enumerate(timestamps):
                eaf.add_annotation("code", ts[0], ts[1])
                eaf.add_annotation("code_num", ts[0], ts[1], value=str(i+1))
                eaf.add_annotation("on_off", ts[0], ts[1], value="{}_{}".format(ts[0], ts[1]))
                eaf.add_annotation("context", ts[0] - 120000, ts[1] + 60000)
                selected = selected.append({'aclew_id': aclew_id,
                                            'corpus': corpus,
                                            'clip_num': i+1,
                                            'onset': ts[0],
                                            'offset': ts[1]},
                                           ignore_index=True)
            eaf.to_file(os.path.join(output_dir, corpus, "{}.eaf".format(aclew_id)))
            shutil.copy(pfsx_path, os.path.join(output_dir, corpus, "{}.pfsx".format(aclew_id)))

    # selected['clip_num'] = selected['clip_num'].astype(int)
    selected[['aclew_id', 'clip_num', 'onset', 'offset']] = selected[['aclew_id', 'clip_num', 'onset', 'offset']].astype(int)

    selected.to_csv('selected_regions.csv', index=False)



# def generate_templates_from_audio(input_dir, output_dir, sample):
#     for root, dirs, files in os.walk(input_dir):
#         for file in files:
#             if file.endswith(".mp3") or file.endswith(".wav"):
#                 timestamps = splice.choose_onsets(os.path.join(root, file))
#                 timestamps = [(x*60000,y*60000) for x, y in timestamps]
#                 aclew_id = int(file.split(".")[0])
#                 info = sample[sample.aclew_id == aclew_id]
#                 templ_path = choose_template(info)
#                 print timestamps
#                 eaf = pympi.Eaf(templ_path)
#                 eaf.add_tier("code")
#                 eaf.add_tier("context")
#                 # eaf.remove_tier("default")
#                 for ts in timestamps:
#                     eaf.add_annotation("code", ts[0], ts[1])
#                     eaf.add_annotation("context", ts[0]-120000, ts[1]+60000)
#                 eaf.to_file(os.path.join(output_dir, "{}.etf".format(file[:-4])))


if __name__ == "__main__":

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    sample_table = pd.read_csv(sys.argv[3])

    generate_templates(sample_table, output_dir)
