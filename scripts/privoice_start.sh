echo '*** System Starting ... ***'

source venv_pvx/bin/activate

export PYTHONPATH=`pwd`
export PVX_BASE_DIR=`pwd`

echo 'Start Message Bus'
cd bus
python MsgBus.py &
cd ..
sleep 1 

echo 'Start System Skill'
python skills/system_skills/skill_system.py &
sleep 1

echo 'Start Services'
echo ' '
echo 'Intent Service'
python framework/services/intent/intent.py &
sleep 1

echo 'Media Service'
python framework/services/media/media_player.py &
echo ' '
echo 'TTS Service'
python framework/services/tts/tts.py &
sleep 1

echo ' '
echo 'Start System Skills'
python skills/system_skills/skill_volume.py &
python skills/system_skills/skill_fallback.py &
python skills/system_skills/skill_media.py &

echo ' '
echo 'Start Skills Manager'
python framework/services/skill_manager/skill_manager.py &
sleep 1

echo ' '
echo 'Wait Skills Init'
sleep 1
echo ' '
echo 'Start the voice recognizer'
./framework/services/recognizer/recognizer.sh &
sleep 1

echo ' '
echo '** Start User Skills **'
./scripts/start_user_skills.sh
echo '** User skills started **'
echo ' '
echo '*** System Started ***'

#tail -f tmp/logs/intent.log tmp/logs/skills.log tmp/logs/media_player.log

