#!/bin/bash
set -e

CONTENT_DIR=$1
echo "1:($1)"

export CONTENT_DIR=$CONTENT_DIR

cd portal/
sudo pip install -r requirements.txt
python manage.py update_operator_docs