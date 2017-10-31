#!/bin/bash
set -e

DOCS_LOCATION=$1
DESTINATION_DIR=$2

echo "Generating blog documentation at $DOCS_LOCATION to $DESTINATION_DIR"
cd "$DOCS_LOCATION"

which bundle
echo "listing from within PPO"
gem list

[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"
rvm use 2.4.1
ruby --version

which ruby
bundle exec jekyll build

cp -r ./_site/* $DESTINATION_DIR

echo "show generated blog"
ls $DESTINATION_DIR
