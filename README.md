# cuddel-mzml2isa-enhance

Repository for CUDDEL work on creating a `mzml_metadata` enhancement function to insert metadata from `mzml2isa` into the output of the ISA Create agent.

Relates to work on https://github.com/gigascience/cuddel-gsk-dataset/

Run with something like:
```
python mzml2isa_enhance.py test-isa/ tmp/ mzml2isa_mapping.json
```
Requires `isaagents==0.10.2`.
