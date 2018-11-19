#!/bin/bash
pip install -e ".[test, examples]" .
jupyter nbextension install --py --symlink --sys-prefix pysbjupyter
jupyter nbextension enable --py --sys-prefix pysbjupyter
jupyter notebook
