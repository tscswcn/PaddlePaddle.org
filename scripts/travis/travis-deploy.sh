#!/bin/bash
set -e

export DEC_PASSWD="1234"

# if [ "$TRAVIS_BRANCH" != "develop" ]; then
#     exit
# fi

# deploy to remote server
openssl aes-256-cbc -d -a -in $TRAVIS_BUILD_DIR/scripts/travis/ubuntu.pem.enc -out ubuntu.pem -k $DEC_PASSWD

eval "$(ssh-agent -s)"
chmod 400 ubuntu.pem

ssh-add ubuntu.pem

ssh -i ubuntu.pem ubuntu@$DEPLOY_IP 'bash -s' < $TRAVIS_BUILD_DIR/scripts/travis/ubuntu-docker-deploy.sh

chmod 644 ubuntu.pem
rm ubuntu.pem