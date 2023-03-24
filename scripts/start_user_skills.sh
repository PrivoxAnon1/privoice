#!/bin/bash

ORIG=`pwd`
for d in skills/user_skills/*/ ; do

    echo "Starting skill ** $d **"

    cd $d
    SKILL_DIR=`pwd`

    [ -d "venv_skill" ] && source venv_skill/bin/activate
    #source venv_skill/bin/activate

    python __init__.py $SKILL_DIR &

    [ -d "venv_skill" ] && deactivate
    #deactivate

    cd $ORIG

done

