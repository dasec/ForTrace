#!/bin/bash
mydir=$(dirname "$0")
source "$mydir"/venv/bin/activate
python3 "$mydir"/validator.py "$@"