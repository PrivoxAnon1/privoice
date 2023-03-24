ORIG=`pwd`

cd $1
SKILL_DIR=`pwd`

[ -d "venv_skill" ] && source venv_skill/bin/activate
#source venv_skill/bin/activate

python __init__.py $SKILL_DIR &

[ -d "venv_skill" ] && deactivate
#deactivate

cd $ORIG

