#!/bin/bash
set -e

DOCS_LOCATION=$1
DESTINATION_DIR=$2

echo "Generating blog documentation at $DOCS_LOCATION to $DESTINATION_DIR"
cd "$DOCS_LOCATION"

which bundle
echo "listing from within PPO"
gem list

bundle exec jekyll build

cp -r ./_site/ $DESTINATION_DIR

echo "show generated blog"
ls $DESTINATION_DIR