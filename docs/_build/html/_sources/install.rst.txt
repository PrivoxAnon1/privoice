Install PriVoice
****************

.. toctree::
   :maxdepth: 2


.. _installation:

============
Installation
============
Note PriVoice currently only runs on a linux system. You can run it
on systems like the Raspberry Pi but it is recommended you run PriVoice
on a reasonable hardware platform with decent quality audio (mic and
speaker or headset). The Pi is a bit underpowered to run speech to text 
and text to speech locally though solutions do exist. 

If your system is hardware constrained and can not run the voice 
assistant locally you should consider using standard http post
commands leveraging the Privox Cloud based voice network. 

=============
Verify System 
=============
Before getting started it is a good idea to make sure you have a properly
configured system. PriVoice basically requires two standard linux commands;
'aplay' and 'arecord' (ALSA play and ALSA record). To make sure everything
is working correctly open a terminal and enter this command


.. code-block:: bash

   arecord -f s16_le -r 16000 -c 2 test.wav

Then say something and hit CTL+C to stop the recording. Next enter this command

.. code-block:: bash

   aplay test.wav

You should hear what you just recorded. If you don't this will need to be 
corrected before you can continue. See the `Installation Issues`_. section 
below for more help with this.


==========
Clone Repo
==========
Assuming the commands 'arecord' and 'aplay' work as expected, you install the system as follows 

.. code-block:: bash

   # checkout the repository
   git clone https://github.com/PrivoxAnon1/privoice.git

   # change into base directory 
   cd privoice

   # run the installation script
   ./scripts/linux_install.sh

You may be asked for your sudo password as it will install ffmpeg and mpg123 if not 
already installed. These are system applications, not Python modules.

The install script will create a new virtual environment and install everything 
into the virtual environment.

The installation should take anywhere from 2 minutes to 20 minutes depending on your system.
Once it has completed you should see something like this on your screen 

.. code-block:: bash

   Successfully uninstalled numba-0.56.4
   Successfully installed Babel-2.12.1 TTS-0.12.0 Werkzeug-2.2.3 anyascii-0.3.2 audioread-3.0.0 cffi-1.15.1 click-8.1.3 contourpy-1.0.7 coqpit-0.0.17 cycler-0.11.0 cython-0.29.28 dateparser-1.1.7 decorator-5.1.1 docopt-0.6.2 flask-2.2.3 fonttools-4.39.2 fsspec-2023.3.0 g2pkk-0.1.2 gruut-2.2.3 gruut-ipa-0.13.0 gruut-lang-de-2.0.0 gruut-lang-en-2.0.0 inflect-5.6.0 itsdangerous-2.1.2 jamo-0.4.1 jieba-0.42.1 joblib-1.2.0 jsonlines-1.2.0 kiwisolver-1.4.4 librosa-0.8.0 llvmlite-0.38.1 matplotlib-3.7.1 mecab-python3-1.0.5 networkx-2.8.8 nltk-3.8.1 num2words-0.5.12 numba-0.55.2 numpy-1.22.4 packaging-23.0 pandas-1.5.3 pillow-9.4.0 platformdirs-3.1.1 pooch-1.7.0 protobuf-3.19.6 psutil-5.9.4 pycparser-2.21 pynndescent-0.5.8 pyparsing-3.0.9 pypinyin-0.48.0 pysbd-0.3.4 python-crfsuite-0.9.9 python-dateutil-2.8.2 pytz-2022.7.1 pytz-deprecation-shim-0.1.0.post0 pyyaml-6.0 resampy-0.4.2 scikit-learn-1.2.2 scipy-1.10.1 six-1.16.0 soundfile-0.12.1 tensorboardX-2.6 threadpoolctl-3.1.0 torchaudio-2.0.1 trainer-0.0.20 tzdata-2022.7 tzlocal-4.3 umap-learn-0.5.1 unidic-lite-1.0.8
   PriVoice Install Complete
   Ended at 
   Sat Mar 18 03:46:56 PM EDT 2023
   Installing default skills
   Cloning into 'privoice_skills'...
   remote: Enumerating objects: 27, done.
   remote: Counting objects: 100% (27/27), done.
   remote: Compressing objects: 100% (24/24), done.
   remote: Total 27 (delta 0), reused 24 (delta 0), pack-reused 0
   Receiving objects: 100% (27/27), 162.74 KiB | 1.37 MiB/s, done.
   Default skills installed


===================
Installation Issues
===================
Installation issues tend to fall into one of several categories; software modules, Linux device names or ALSA names.


Software modules like Pytorch may not install properly on lower end systems or uncommon environments like a Kendryte
Risc board or Raspberry Pi. In this case you will need to figure out how to get the module installed in your 
environment. Isolating the module and just getting one module at a time to install is usually the best approach.

Linux device names are the names used by the *aplay* and *arecord* commands. In most cases you will not need to 
worry about this, but if you do there is an entry in the **yava.yml** file which holds this value and you can simply 
set it there. This value is the value used with the '-D' command line parameter. For example 


.. code-block:: bash

   aplay -D plughw:VF_ASR_(L)

If you leave this value blank no '-D' will be added to the command line for the *aplay* command which in most cases is what you want. See the `Device Names`_ section below for more information.

ALSA names are used to control the input and output device levels. These are typically the microphone and speaker. If these are not set correctly PriVoice will not be able to change the volume. See the section below on `ALSA Names`_ for more information.

------------
Device Names
------------
If either *arecord* or *aplay* are not working you will need to correct this first. These are foundational to the system. 

Assuming you have hardware and it is working the most likely issue is the '.asourdrc' file. This can be worked around 
by setting the device name in the **yava.yml** file. Finding the correct device name can be a pain. For example here is
the output of the command **'aplay -L'** on one laptop ...


.. code-block:: bash

  null
    Discard all samples (playback) or generate zero samples (capture)
  default
    Playback/recording through the PulseAudio sound server
  samplerate
    Rate Converter Plugin Using Samplerate Library
  speexrate
    Rate Converter Plugin Using Speex Resampler
  jack
    JACK Audio Connection Kit
  oss
    Open Sound System
  pulse
    PulseAudio Sound Server
  upmix
    Plugin for channel upmix (4,6,8)
  vdownmix
    Plugin for channel downmix (stereo) with a simple spacialization
  hw:CARD=NVidia,DEV=3
    HDA NVidia, HDMI 0
    Direct hardware device without any conversions
  hw:CARD=NVidia,DEV=7
    HDA NVidia, HDMI 1
    Direct hardware device without any conversions
  hw:CARD=NVidia,DEV=8
    HDA NVidia, HDMI 2
    Direct hardware device without any conversions
  hw:CARD=NVidia,DEV=9
    HDA NVidia, HDMI 3
    Direct hardware device without any conversions
  plughw:CARD=NVidia,DEV=3
    HDA NVidia, HDMI 0
    Hardware device with all software conversions
  plughw:CARD=NVidia,DEV=7
    HDA NVidia, HDMI 1
    Hardware device with all software conversions
  plughw:CARD=NVidia,DEV=8
    HDA NVidia, HDMI 2
    Hardware device with all software conversions
  plughw:CARD=NVidia,DEV=9
    HDA NVidia, HDMI 3
    Hardware device with all software conversions
  hdmi:CARD=NVidia,DEV=0
    HDA NVidia, HDMI 0
    HDMI Audio Output
  hdmi:CARD=NVidia,DEV=1
    HDA NVidia, HDMI 1
    HDMI Audio Output
  hdmi:CARD=NVidia,DEV=2
    HDA NVidia, HDMI 2
    HDMI Audio Output
  hdmi:CARD=NVidia,DEV=3
    HDA NVidia, HDMI 3
    HDMI Audio Output
  dmix:CARD=NVidia,DEV=3
    HDA NVidia, HDMI 0
    Direct sample mixing device
  dmix:CARD=NVidia,DEV=7
    HDA NVidia, HDMI 1
    Direct sample mixing device
  dmix:CARD=NVidia,DEV=8
    HDA NVidia, HDMI 2
    Direct sample mixing device
  dmix:CARD=NVidia,DEV=9
    HDA NVidia, HDMI 3
    Direct sample mixing device
  usbstream:CARD=NVidia
    HDA NVidia
    USB Stream Output
  hw:CARD=Generic,DEV=3
    HD-Audio Generic, HDMI 0
    Direct hardware device without any conversions
  plughw:CARD=Generic,DEV=3
    HD-Audio Generic, HDMI 0
    Hardware device with all software conversions
  hdmi:CARD=Generic,DEV=0
    HD-Audio Generic, HDMI 0
    HDMI Audio Output
  dmix:CARD=Generic,DEV=3
    HD-Audio Generic, HDMI 0
    Direct sample mixing device
  usbstream:CARD=Generic
    HD-Audio Generic
    USB Stream Output
  hw:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    Direct hardware device without any conversions
  plughw:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    Hardware device with all software conversions
  sysdefault:CARD=Generic_1
    HD-Audio Generic, ALC3254 Analog
    Default Audio Device
  front:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    Front output / input
  surround21:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    2.1 Surround output to Front and Subwoofer speakers
  surround40:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    4.0 Surround output to Front and Rear speakers
  surround41:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    4.1 Surround output to Front, Rear and Subwoofer speakers
  surround50:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    5.0 Surround output to Front, Center and Rear speakers
  surround51:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
  surround71:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
  dmix:CARD=Generic_1,DEV=0
    HD-Audio Generic, ALC3254 Analog
    Direct sample mixing device
  usbstream:CARD=Generic_1
    HD-Audio Generic
    USB Stream Output
  usbstream:CARD=acp
    acp
    USB Stream Output

The command **arecord -L** shows the same for the input devices on your system.
**Note!** - if you change the recording device (for *arecord*) you **must** also manually
edit the file *framework/services/recognizer/recognizer.sh* as follows ...

.. code-block:: bash

   Change the line 
     arecord -f s16_le -c 1 -r 16000 | python -W ignore framework/services/recognizer/recognizer.py

   To
     arecord -DDEVICE_NAME -f s16_le -c 1 -r 16000 | python -W ignore framework/services/recognizer/recognizer.py


Where DEVICE_NAME is the device name you need to use with the *arecord* utility. In other words 
we are adding a device name to the command line we use to execute the recognizer.

You can also run 

.. code-block:: bash

   python test/list_input_devices.py

To get a list of device names on your system. Of course this won't run unless you are in your base directory and you have previously run 

.. code-block:: bash

   . ./scripts/init_env.sh


Hopefully your output is far less than the output shown above (it usually is). Regardless, you will need to test each device name until you hit the correct one.
It should be noted the device name must be derived from the output by combining some of the output. This amounts to removing the 
'CARD=' from the output line. For example using the output line

.. code-block:: bash

  plughw:CARD=Generic_1,DEV=0

You would test this device as follows 

.. code-block:: bash

  aplay -Dplughw:Generic_1,DEV=0


And for the following entry 

.. code-block:: bash

  plughw:CARD=NVidia,DEV=3

You would test this device as follows 

.. code-block:: bash

  aplay -Dplughw:NVidia,DEV=3

----------
ALSA Names
----------
The ALSA mixer is used to control the volume. If the default install does not allow you to set the volume you will probably need to set the value in the **yava.yml** file. 

Finding the ALSA mixer name for your speaker and microphone is often not straightforward. For example, here is some ALSA mixer output from a laptop

.. code-block:: bash

  $ amixer scontrols

  Simple mixer control 'IEC958',0
  Simple mixer control 'IEC958',1
  Simple mixer control 'IEC958',2
  Simple mixer control 'IEC958',3

  $ amixer -c 0 scontrols

  Simple mixer control 'IEC958',0
  Simple mixer control 'IEC958',1
  Simple mixer control 'IEC958',2
  Simple mixer control 'IEC958',3

  $ amixer -c 1 scontrols

  Simple mixer control 'Mic ACP LED',0
  Simple mixer control 'IEC958',0

  $ amixer -c 2 scontrols

  Simple mixer control 'Master',0
  Simple mixer control 'Headphone',0
  Simple mixer control 'Headphone Mic Boost',0
  Simple mixer control 'Speaker',0
  Simple mixer control 'PCM',0
  Simple mixer control 'Mic ACP LED',0
  Simple mixer control 'Capture',0
  Simple mixer control 'Capture',1
  Simple mixer control 'Auto-Mute Mode',0
  Simple mixer control 'Digital',0
  Simple mixer control 'Headset Mic Boost',0
  Simple mixer control 'Input Source',0
  Simple mixer control 'Input Source',1

  $ amixer -c 3 scontrols

Again, hopefully your system is not quite as complex, but what we are ultimately looking for are the Mic and Speaker control names. 
In my case the values I am looking for are 'Speaker' and 'Capture'. You can verify by running the 'amixer sget' command like this 


.. code-block:: bash

  $ amixer -c 2 sget Speaker
  Simple mixer control 'Speaker',0
    Capabilities: pvolume pswitch
    Playback channels: Front Left - Front Right
    Limits: Playback 0 - 87
    Mono:
    Front Left: Playback 87 [100%] [0.00dB] [on]
    Front Right: Playback 87 [100%] [0.00dB] [on]

And for the microphone 

.. code-block:: bash

  $ amixer -c 2 sget Capture
  Simple mixer control 'Capture',0
    Capabilities: cvolume cswitch
    Capture channels: Front Left - Front Right
    Limits: Capture 0 - 63
    Front Left: Capture 63 [100%] [30.00dB] [off]
    Front Right: Capture 63 [100%] [30.00dB] [off]

In most cases you will probably not need the '-c' (card) option. In this case the command would be 

.. code-block:: bash

  $ amixer sget Speaker
  Simple mixer control 'Speaker',0
    Capabilities: pvolume pswitch
    Playback channels: Front Left - Front Right
    Limits: Playback 0 - 87
    Mono:
    Front Left: Playback 87 [100%] [0.00dB] [on]
    Front Right: Playback 87 [100%] [0.00dB] [on]

You can run this command which will try to auto-detect your card and master control. 

.. code-block:: bash

  $ python test/find_volume_control.py

  Found card 2 ---> Simple mixer control 'Master',0

  To change your volume use this command amixer -c 2 sset Master 75%

Note - the entire combination must be entered in the **yava.yml** file. For example 

.. code-block:: bash

  - Advanced:
    CrappyAEC: n
    MasterControlName: "-c 2 'Master'"
    InputDeviceName: ''
    InputLevelControlName: "-c 2 'Capture'"
    LogLevel: i
    OutputDeviceName: ''
    OutputLevelControlName: "-c 2 'Speaker'"
    Platform: l


Or if no card is required you can drop the "-c".

.. code-block:: bash

  - Advanced:
    CrappyAEC: n
    MasterControlName: "'Master'"
    InputDeviceName: ''
    InputLevelControlName: "'Capture'"
    LogLevel: i
    OutputDeviceName: ''
    OutputLevelControlName: "'Speaker'"
    Platform: l


----------------
Software Modules
----------------
Typically issues arise from pinned version clash. If you are seeing a module build error you should create a new virtual environment and try to install it in isolation there first.

===============
Test and Adjust
===============
Once you have verified the installation completed successfully you should test
the quality of your hardware. Run the following command from the base directory

.. code-block:: bash

   . ./scripts/init_env.sh

Yes, that's **dot space dot slash**. Next run 

.. code-block:: bash

   ./framework/services/recognizer/recognizer.sh


This will run the recognizer using the default system configuration values.
You should see what you say printed on the screen. Your output should look
similar to this

.. code-block:: bash

   Recording WAVE 'stdin' : Signed 16 bit Little Endian, Rate 16000 Hz, Mono
   STT Transcriber is Running
   BUS:Not Connected, MIN_WAV:9600 bytes, VAD:1, MODEL:small.en, RST:3.5 seconds
   [58240][1.820000 secs]Took 1.303991 secs: Testing, one, two, three.
   [25600][0.800000 secs]Took 0.200814 secs: Goodbye.

Hit Ctl+C at any time to exit the program.

The output shown above lists several important values. 

First, the numbers 58240 and 25600 represent the size of the wav data produced by your utterance. Since we sample two bytes 16,000 times a second we camn simply use this to convert to seconds of input which is the next number shown, followed by how long it took to transcribe that wav data into a text string. 

From the output we can see that using the *small.en* model we are getting close to a 1:1 ratio of input time to transcribe time. 

If we were to change the STT model in the **yava.yml** file to *tiny.en* and restart we would expect to see the time to transcribe decrease along with the accuracy. The required memory for the *tiny.en* model is below 1GB. 

You should experiment with this setting until you are satisfied it is working in a manner that is agreeable to you. In some cases you may prefer speed over accuracy, etc. It is important to verify your wake word is being picked up consistently. Poor wake word selection will cause poor activation. Wake words should be somewhat rare in your normal lexicon to reduce false activations. They should also have some distinctive characteristics like a hard consonant or two, or some distinctive quality.

==================
Operational Issues
==================

---------------
Memory Concerns
---------------
Nothing is more disappointing than seeing the following output 

.. code-block:: bash

  $ ./framework/services/recognizer/recognizer.sh 
  Recording WAVE 'stdin' : Signed 16 bit Little Endian, Rate 16000 Hz, Mono
  Traceback (most recent call last):
    File "/PriVoice/framework/services/recognizer/recognizer.py", line 159, in <module>
      sd = SilenceDetector()
    File "/PriVoice/framework/services/recognizer/recognizer.py", line 65, in __init__
      self.model = whisper.load_model(self.model_name)
    File "/PriVoice/venv_pvx/lib/python3.10/site-packages/whisper/__init__.py", line 122, in load_model
      return model.to(device)
    File "/PriVoice/venv_pvx/lib/python3.10/site-packages/torch/nn/modules/module.py", line 989, in to
      return self._apply(convert)
    File "/PriVoice/venv_pvx/lib/python3.10/site-packages/torch/nn/modules/module.py", line 641, in _apply
      module._apply(fn)
    File "/PriVoice/venv_pvx/lib/python3.10/site-packages/torch/nn/modules/module.py", line 641, in _apply
      module._apply(fn)
    File "/PriVoice/venv_pvx/lib/python3.10/site-packages/torch/nn/modules/module.py", line 641, in _apply
      module._apply(fn)
    [Previous line repeated 2 more times]
    File "PriVoice/venv_pvx/lib/python3.10/site-packages/torch/nn/modules/module.py", line 664, in _apply
      param_applied = fn(param)
    File "/PriVoice/venv_pvx/lib/python3.10/site-packages/torch/nn/modules/module.py", line 987, in convert
      return t.to(device, dtype if t.is_floating_point() or t.is_complex() else None, non_blocking)
  torch.cuda.OutOfMemoryError: CUDA out of memory. Tried to allocate 26.00 MiB (GPU 0; 3.81 GiB total capacity; 3.02 GiB already allocated; 3.44 MiB free; 3.27 GiB reserved in total by PyTorch) If reserved memory is >> allocated memory try setting max_split_size_mb to avoid fragmentation.  See documentation for Memory Management and PYTORCH_CUDA_ALLOC_CONF

Ouch, my GPU ran out of memory. What happened? It has like 4GB.

The STT models require anywhere from just under 1GB to upwards of 10GB of memory. If you get an out of memory message you will need to use a smaller model. If you run the model on your GPU (this is automatically determined by PyTorch though there are ways to overide this) you will be limited to the GPU RAM. 

For example if a laptop has 4GB of GPU RAM it can only run the small model and under, however, if you disable the GPU you can run any model that fits in your available memory. Of course this assumes your CPU has more memory available than your GPU. If your system has more than 32GB of RAM you should be able to run any model. 

In general the *tiny* model works fine for most applications but you can always edit the **yava.yml** file and change the model. 

STT models have several attributes ...

+ Transcription Speed
+ Transcription Accuracy
+ Memory Consumption

To change the model simply change the Recognizer:ModelName value in the **yava.yml** file. 
In the output below, the value is set to *small.en*.

.. code-block:: bash

    Recognizer:
      # vad mode controls silence
      # detection sensitivity.
      # 1=loose, 3=tight
      VadMode: 1

      # least number of bytes required to
      # be considered a valid utterance
      # warning, too short and you will
      # things like 'stop' and 'up'
      MinUtteranceBytes: 9600

      # the whisper model
      ModelName: 'small.en'

      # how long to allow the transcriber to

Supported values are 

+ tiny
+ tiny.en
+ base
+ base.en
+ small
+ small.en
+ medium
+ medium.en
+ large
+ large-v2

-----------------
Microphone Issues
-----------------
Another source of pain if often the microphone level. If you are running a desktop you can simply use the toolbar to set your microphone level, however, on headless systems you need to use the command line.

The *amixer* command does not always set the microphone level correctly but the *pacmd* utility seems to work well when present.
There are two helpful files in the *test/* subdirectory. They allow you to *set* and *get* the microphone level using the *pacmd* command. 

.. code-block:: bash

  $ python test/get_mic_pacmd.py
  32127

  $ python test/set_mic_pacmd.py 65000

  $ python test/get_mic_pacmd.py
  65000

You should set the microphone to around 32000 and then run the recognizer (./framework/services/recognizer/recognizer.sh) and see how well your voice is being recognized.
You can either stop the recognizer and then set the volume and rerun the recognizer or you can open a second terminal and change the volume while the recognizer is running in the first terminal.

