System Configuration
********************

.. toctree::
   :maxdepth: 2

.. _configuration:

=============
Configuration
=============
PriVoice configuration is controlled by the file named 'yava.yml' which may be found in the base directory. This is a standard yaml file and may be edited freely. This file contains many parameters, most of which should not be modified. Important entries are shown below. 

================
Basic Parameters
================
+ **Advanced.STT.VadMode**

  VAD Mode controls the sensitivity of the silence detector. The value controls how quickly it detects silence. Allowable values are 1 (loose), 2 (normal) or 3 (tight).

+ **Advanced.STT.ModelName**

  Model Name controls the STT model used to transcribe audio data to text. Allowable values are 

  1. tiny

  2. tiny.en

  3. base

  4. base.en

  5. small

  6. small.en

  7. medium

  8. medium.en

  9. large

  10. large-v2

The models are shown in order of least accurate (tiny) to most accurate (large-v2). It is also the case
that as accuracy increases, so does the amount of time necessary to perform the transcription. So for
example using the 'large' model may take up to 20 times longer to perform the transcription.

+ **Basic.WakeWords**

  This is a list of one or more wake words you want to use to put the assistant in 'activate' mode. For example, by default the system is configured to use the word 'computer' as the wake word. The config file section is shown below. 

.. code-block:: bash

    WakeWords:
    - hey computer
    - computer

To use the name 'Jarvis' as the wake word, edit this section to look like this.

.. code-block:: bash

    WakeWords:
    - hey jarvis
    - yo jarvis
    - jarvis


===================
Advanced Parameters
===================

