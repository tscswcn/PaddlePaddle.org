#!/bin/bash
set -e

DOCS_LOCATION=$1
DESTINATION_DIR=$2

echo "Generating visualdl documentation at $DOCS_LOCATION to $DESTINATION_DIR"
cd "$DOCS_LOCATION"

# Create the build directory for CMake.
mkdir -p $DOCS_LOCATION/build
cd $DOCS_LOCATION/build

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

# Compile Documentation only.
cmake "$DOCS_LOCATION" -DWITH_DOC=ON
make -j $processors visualdl_docs_en
make -j $processors visualdl_docs_cn

mkdir -p $DESTINATION_DIR

cp -r $DOCS_LOCATION/build/docs/* $DESTINATION_DIR/.

