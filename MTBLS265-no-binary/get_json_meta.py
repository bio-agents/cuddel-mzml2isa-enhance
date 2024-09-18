# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
from mzml2isa.mzml import mzMLmeta
import json
import os
data_dir = '.'

out_dir = 'json_meta'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

print(os.listdir(data_dir))
for i, mzml in enumerate(os.listdir(data_dir)):
    if not mzml.lower().endswith('.mzml'):
        continue
    mzml_pth = os.path.join(data_dir, mzml)
    mz = mzMLmeta(mzml_pth)

    mzml_name, mzml_ext = os.path.splitext(mzml_pth)

    with open(os.path.join(out_dir, "{}.json".format(os.path.basename(mzml_name))), "w") as outfile:
        json.dump(mz.meta,  outfile, indent=4)
