ORIG=`pwd`

cd $1
SKILL_DIR=`pwd`
source venv_skill/bin/activate
python __init__.py $SKILL_DIR

cd $ORIG
deactivate

