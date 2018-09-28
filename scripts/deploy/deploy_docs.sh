#!/bin/bash
set -e

DEC_PASSWD=$1
GITHUB_BRANCH=$2
SOURCE_DIR=$3
PPO_BRANCH=$5

echo "Deploy docs: DEC_PASSWD:($1) GITHUB_BRANCH:($2) SOURCE_DIR:($3) PPO_BRANCH:($5)"
echo "1. Pull PaddlePaddle.org app."
curl -LOk https://github.com/PaddlePaddle/PaddlePaddle.org/archive/$PPO_BRANCH.zip
unzip -q $PPO_BRANCH.zip
cd PaddlePaddle.org-$PPO_BRANCH/portal

echo "2. Install needed pip packages."
if ! [ -x "$(which sudo)" ]; then
pip install --ignore-installed -r requirements.txt
else
sudo pip install --ignore-installed -r requirements.txt
fi

mkdir documentation

# We need to set this env so the deploy script knows whether or not this
# is a local development build.
export ENV=production

echo "3. Executing deploy_documentation."
python manage.py deploy_documentation --source_dir=$SOURCE_DIR --destination_dir=documentation $GITHUB_BRANCH

echo "4. Copying remote documentation here first to be ready for indexing."
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

# Merge the documentations, and temporarily swap spots.
VERSION=$(python -c "from portal.management.commands.utils import sanitize_version; print sanitize_version('$GITHUB_BRANCH')")
mkdir -p indexable-documentation/$VERSION
rsync -r content_mgr@$STAGE_DEPLOY_IP:/var/pages/documentation/$VERSION indexable-documentation/$VERSION
cp -rf documentation/$VERSION/ indexable-documentation/$VERSION
mv documentation new-documentation
mv indexable-documentation documentation

echo "5. Build the search index of the newly generated documentation."
# Need to do this because on Ubuntu node installs as nodejs.
ln -s /usr/bin/nodejs /usr/bin/node

python manage.py rebuild_index en $GITHUB_BRANCH
python manage.py rebuild_index zh $GITHUB_BRANCH
mv documentation indexable-documentation
mv new-documentation documentation

echo "6. Documentation generation completed."
# Display what documentation will be sync to the server
ls documentation

echo "5. Prepare to rsync documentation."
rsync -r documentation/ content_mgr@$STAGE_DEPLOY_IP:/var/pages/documentation
rsync -r /var/pages/menus/ content_mgr@$STAGE_DEPLOY_IP:/var/pages/menus
rsync -r /var/pages/indexes/ content_mgr@$STAGE_DEPLOY_IP:/var/pages/indexes

echo "6. Documentation deployed. Clean up."
chmod 644 content_mgr.pem
rm -rf documentation
rm -rf indexable-documentation
rm -rf /var/pages/menus
rm -rf /var/pages/indexes
