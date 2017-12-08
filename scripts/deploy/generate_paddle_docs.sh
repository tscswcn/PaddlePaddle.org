#!/bin/bash
set -e

DOCS_LOCATION=$1
DESTINATION_DIR=$2

echo "Generating paddle documentation at $DOCS_LOCATION to $DESTINATION_DIR"
cd "$DOCS_LOCATION"

# Create the build directory for CMake.
mkdir -p $DOCS_LOCATION/build
cd $DOCS_LOCATION/build

find . -name "CMakeCache.txt" -exec rm -R {} \;

if [ ! -d "$DESTINATION_DIR" ]; then
    echo "Directory $DESTINATION_DIR does not exists, creating..."
    mkdir -p $DESTINATION_DIR
fi

processors=1
if [ "$(uname)" == "Darwin" ]; then
    processors=`sysctl -n hw.ncpu`
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    processors=`nproc`
fi

# Disable paddle fluid and paddle operators docs for now, since the build does not currently work
# TODO[thuan]: Make document generator work with paddle fluid and paddle operators docs

# Compile Documentation only.
cmake "$DOCS_LOCATION" -DCMAKE_BUILD_TYPE=Debug -DWITH_GPU=OFF -DWITH_MKL=OFF -DWITH_DOC=ON
make -j $processors gen_proto_py
#make -j $processors paddle_python
make -j $processors paddle_docs paddle_docs_cn
#make -j $processors print_operators_doc
#paddle/pybind/print_operators_doc > doc/en/html/operators.json

mkdir -p $DESTINATION_DIR

cp -r $DOCS_LOCATION/build/doc/* $DESTINATION_DIR/.

