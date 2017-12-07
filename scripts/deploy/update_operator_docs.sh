#!/bin/bash
set -e

git clone https://github.com/PaddlePaddle/Paddle.git
cd Paddle
docker run -it -v `pwd`:/paddle paddlepaddle/paddle:latest-dev bash
cd /paddle
mkdir build
cd build
cmake -DWITH_GPU=OFF -DWITH_TESTING=OFF -DWITH_DOC=ON ..
make print_operators_doc
chmod +x ./paddle/pybind/print_operators_doc
./paddle/pybind/print_operators_doc
