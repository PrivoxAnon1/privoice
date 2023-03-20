#!/bin/bash

ORIG=`pwd`
for d in tmp/privoice_skills/*/ ; do

    echo "Installing skill ** $d **"

    dir=$d
    dir="${dir%/}"             # strip trailing slash (if any)
    subdir="${dir##*/}"
    subdir="skills/user_skills/"$subdir

    bash scripts/install_skill.sh $d $subdir

    cd $ORIG
    #deactivate

done

