#!/bin/bash
set -e

# Builds the docker image for PaddlePaddle.org

docker --version  # document the version travis is using
docker build -t paddlepaddle.org .