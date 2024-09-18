from isaagents import isatab
from isaagents.model import *
import sys
import json
import os

input_filepath = sys.argv[1]  # input path to ISA-Tab
output_filepath = sys.argv[2]  # output path to write ISA-Tab
mapping_filepath = sys.argv[3]  # path to mapping json file

ISA = isatab.load(input_filepath)

# only get first assay from first study obj
study = ISA.studies[0]

mapping = {}
with open(mapping_filepath) as fp:
    mapping = json.load(fp)

for assay in study.assays:
    # get mass spectrometry processes only
    ms_processes = [x for x in assay.process_sequence
                    if x.executes_protocol.protocol_type.term == 'mass spectrometry']
    # insert the new parameter values
    for k, v in mapping.items():
        with open(os.path.join('MTBLS265-no-binary', 'json_meta', v + '.json')) as fp2:
            mzml_meta = json.load(fp2)
            data_trans_meta = {k: v for k, v in mzml_meta.items() if
                               k.startswith('Data Transformation')}
            labels = {k: v for k, v in mzml_meta.items() if
                k.endswith(('File', 'Name'))}
            ms_prot_meta = {k: v for k, v in mzml_meta.items() if
                            not k.startswith('Data Transformation') and
                            k not in labels.keys()}
        try:  #  add parameter values to MS process
            ms_process = [x for x in ms_processes if k in [y.filename for y in x.outputs]][0]
            pvs = ms_process.parameter_values
            for item in ms_prot_meta:
                if not ms_process.executes_protocol.get_param(item):
                    ms_process.executes_protocol.add_param(item)
                param = ms_process.executes_protocol.get_param(item)
                meta_item = ms_prot_meta[item]
                if 'value' in meta_item.keys():
                    value = meta_item['value']  # check for unit as well
                elif 'name' in meta_item.keys():
                    value = meta_item['name']  # check for ontology annotation
                elif 'entry_list' in meta_item.keys():
                    values = meta_item['entry_list']
                    if 'value' in values[-1].keys():
                        value = values[-1]['value']  # check for unit as well
                    elif 'name' in values[-1].keys():
                        value = values[-1]['name']  # check for ontology annotation
                    else:
                        raise IOError(values[-1])
                else:
                    raise IOError(meta_item)
                pv = ParameterValue(category=param, value=value)
                ms_process.parameter_values.append(pv)

            #  set raw file name to mzML meta raw file name and sample name too
            for output in ms_process.outputs:
                if output.label in labels.keys():
                    output.filename = labels[
                    output.label]['entry_list'][-1]['value']
                    output.generated_from[-1].name = labels[
                    'Sample Name']['value']
            #  set MS Assay Name to mzML metadata
            ms_process.name = labels['MS Assay Name']['value']

            #  add data transformation to describe conversion to mzML
            if data_trans_meta['Data Transformation Name']:
                if not study.get_prot('Conversion to mzML'):
                    dt_prot = Protocol(name='Conversion to mzML',
                        protocol_type=OntologyAnnotation(
                        term='data transformation'))
                    dt_prot.add_param('peak picking')
                    dt_prot.add_param('software')
                    dt_prot.add_param('software version')
                    study.protocols.append(dt_prot)
                dt_prot = study.get_prot('Conversion to mzML')
                dt_process = Process(executes_protocol=dt_prot)
                dt_process.outputs = [DerivedSpectralDataFile(
                    filename=labels['Derived Spectral Data File'][
                        'entry_list'][-1]['value'])]
                dt_process.inputs = ms_process.outputs
                plink(ms_process, dt_process)
                assay.process_sequence.append(dt_process)
        except IndexError:
            pass

isatab.dump(ISA, output_filepath)
