#!/bin/bash

ORIG=`pwd`

# Usage: ./install_skill.sh source_dir destination_dir

SOURCE=$1
DEST=$2

# copy code
cp -r $1/ $2/

# create virtual enviornment
cd $2

python3 -m venv venv_skill
source venv_skill/bin/activate
cat $ORIG/scripts/default_skill_requirements.txt >> requirements.txt
pip install -r requirements.txt

cd $ORIG
deactivate
