echo 'Started at '
date
#
# should be run from base dir
# Example:
#     ./scripts/linux_install.sh
#
echo 'Begin Installation, PriVoice Version 0.0.1'

sudo apt install python3-dev
sudo apt install build-essential
sudo apt install ffmpeg
sudo apt install curl
sudo apt install wget
sudo apt install mpg123

python3 -m venv venv_pvx
source venv_pvx/bin/activate
pip install --upgrade pip
pip install --upgrade wheel setuptools
pip install setuptools -U

pip install -r scripts/requirements.txt
pip install git+https://github.com/openai/whisper.git

echo 'Installing Local NLP'
cd framework/services/intent/nlp/local
tar xzfv cmu_link-4.1b.tar.gz
cd link-4.1b
make
cd ../../../../../..

# don't know why but seems this is always needed
pip install -U TTS

echo ' '
echo 'PriVoice Install Complete'
echo ' '
echo 'Ended at '
date
echo ' '
echo ' '
echo 'Installing default skills'
echo ' '

cd tmp
git clone https://github.com/PrivoxAnon1/privoice_skills.git
cd ..
bash scripts/install_default_skills.sh
echo ' '
echo 'Default skills installed'
echo ' '

