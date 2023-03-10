#!/bin/bash

ORIG=`pwd`
for d in skills/user_skills/*/ ; do

    echo "Starting skill ** $d **"

    cd $d
    SKILL_DIR=`pwd`
    source venv_skill/bin/activate
    python __init__.py $SKILL_DIR &

    cd $ORIG
    deactivate

done

