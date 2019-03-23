#!/bin/bash
pip install -e ".[test, examples]" .
jupyter nbextension install --py --symlink --sys-prefix pyvipr
jupyter nbextension enable --py --sys-prefix pyvipr
jupyter notebook
