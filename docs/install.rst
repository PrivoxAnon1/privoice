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
corrected before you can continue. See the **Installation Issues** section 
below for more help with this.


=======
Install
=======
Assuming the commands 'arecord' and 'aplay' work as expected, you install the system as follows 

.. code-block:: bash

   # checkout the repository
   git clone https://github.com/PrivoxAnon1/privoice.git

   # change into base directory 
   cd privoice

   # run the installation script
   ./scripts/linux_install.sh

It may ask you for your sudo password as it will install ffmpeg and mpg123 if not 
already installed. These are system applications, not Python modules.

The install script will create a new virtual environment and install everything 
into the virtual environment except for ffmpeg and mpg123 (which is used to play 
mp3 media).

The installation should take anywhere from 2 minutes to 20 minutes depending on your system.
Once it has completed you should see something like this on your screen 

.. code-block:: bash

   bla bla bla
   more bla
   and finally


-------------------
Installation Issues
-------------------

===============
Test and Adjust
===============
Once you have verified the installation completed successfully you should test
the quality of your hardware. Run the following command from the base directory

.. code-block:: bash

   . ./scripts/init_env.sh

Yes, that's dot space dot slash. Next run 

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

------------------
Operational Issues
------------------
The output shown above lists several important values. First, the numbers 58240 and 25600 represent the size of the wav data produced by your utterance. Since we sample two bytes 16,000 times a second we camn simply use this to convert to seconds of input which is the next number shown, followed by how long it took to transcribe that wav data into a text string. 

From the output we can see that using the small.en model we are getting close to a 1:1 ratio of input time to transcribe time. If we were to change the STT model in the yava.yml file to tiny.en and restart we would expect to see the time to transcribe decrease along with the accuracy. You should experiment with this setting until you are satisfied it is working in a manner that is agreeable to you. Some folks prefer speed over accuracy, etc.






