#!/bin/bash

rm -rf dist
python3 setup.py sdist
pip3 install dist/ucsc-cse40-* --user --upgrade --force-reinstall
