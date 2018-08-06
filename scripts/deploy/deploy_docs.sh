#!/bin/bash
set -e

DEC_PASSWD=$1
GITHUB_BRANCH=$2
SOURCE_DIR=$3
PPO_BRANCH=$4

echo "Deploy docs: DEC_PASSWD:($1) GITHUB_BRANCH:($2) SOURCE_DIR:($3) PPO_BRANCH:($4)"
echo "Pull PaddlePaddle.org app"
curl -LOk https://github.com/PaddlePaddle/PaddlePaddle.org/archive/$PPO_BRANCH.zip
unzip $PPO_BRANCH.zip
cd PaddlePaddle.org-$PPO_BRANCH/portal

if ! [ -x "$(which sudo)" ]; then
pip install --ignore-installed -r requirements.txt
else
sudo pip install --ignore-installed -r requirements.txt
fi

mkdir documentation

# We need to set this env so the deploy script knows whether or not this
# is a local development build.
export ENV=production

echo "executing deploy_documentation"
python manage.py deploy_documentation --source_dir=$SOURCE_DIR --destination_dir=documentation $GITHUB_BRANCH

echo "Documentation generation completed"
# Display what documentation will be sync to the server
ls documentation

# Deploy to remote server by SSH'ing into it.
openssl aes-256-cbc -d -a -in ../scripts/deploy/content_mgr.pem.enc -out content_mgr.pem -k $DEC_PASSWD
eval "$(ssh-agent -s)"
chmod 400 content_mgr.pem
ssh-add content_mgr.pem
export STAGE_DEPLOY_IP=13.229.163.131

# To avoid waiting for "Are you sure you want to continue connecting" input
if [ ! -d ~/.ssh ] ; then
mkdir ~/.ssh
fi
ssh-keyscan $STAGE_DEPLOY_IP >> ~/.ssh/known_hosts
rsync -r documentation/ content_mgr@$STAGE_DEPLOY_IP:/var/pages/documentation
rsync -r /var/pages/menus/ content_mgr@$STAGE_DEPLOY_IP:/var/pages/menus

chmod 644 content_mgr.pem
rm -rf documentation
rm -rf /var/pages/menus
