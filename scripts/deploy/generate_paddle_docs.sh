#!/bin/bash
set -e

PADDLE_ROOT = "$( cd "$( dirname "${BASH_SOURCE[0]}")/../../" && pwd )"

echo $PADDLE_ROOT

ls $PADDLE_ROOT

echo $TRAVIS_BUILD_DIR

cd ../../
export PYTHONPATH=`pwd`/Paddle/build/python
