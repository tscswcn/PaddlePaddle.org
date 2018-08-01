#!/bin/bash
set -e

ls $PADDLE_ROOT
pwd
ls $PADDLE_ROOT/build/

export PYTHONPATH=$PADDLE_ROOT/build/python
