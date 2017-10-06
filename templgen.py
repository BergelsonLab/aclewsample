import sys
import os

import splice
import pympi
import pandas as pd

basic_00_07 = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_00-07mo.etf'
basic_08_18 = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_08-18mo.etf'
basic_19_36 = 'data/templates/ACLEW-basic-templates-20170726/ACLEW-basic-template_19-36mo.etf'

casillas_00_07 = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_00-07mo.etf'
casillas_08_18 = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_08-18mo.etf'
casillas_19_36 = 'data/templates/ACLEW-basic-templates-Casillas-20170726/ACLEW-basic-template-Casillas_19-36mo.etf'

conicet_00_07 = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_00-07mo.etf'
conicet_08_18 = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_08-18mo.etf'
conicet_19_36 = 'data/templates/ACLEW-basic-templates-CONICET-20170726/ACLEW-basic-template-CONICET_19-36mo.etf'


def choose_template(info):
    print

def generate_templates(input_dir, output_dir, sample):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".mp3") or file.endswith(".wav"):
                timestamps = splice.choose_onsets(os.path.join(root, file))
                timestamps = [(x*60000,y*60000) for x, y in timestamps]
                aclew_id = file.split(".")[0]
                info = sample[sample.aclew_id == aclew_id]

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
    sample_table = pd.read_csv(sys.argv[3])

    generate_templates(input_dir, output_dir, sample_table)
