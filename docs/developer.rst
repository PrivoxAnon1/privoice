Developer Guide
***************

.. toctree::
   :maxdepth: 2

-------------------
Theory of Operation
-------------------
The system takes input via the microphone using the 'arecord' utility piped out to the speech recognizer. 
The file *framework/services/recognizer/recognizer.sh* demonstrates how this is accomplished.

.. code-block:: bash

   arecord -f s16_le -c 1 -r 16000 | python -W ignore framework/services/recognizer/recognizer.py

The result of this audio input being fed to the recognizer is a series of raw messages sent out the 
message bus with the target being the intent service. 

The intent service converts raw messages to qualified messages. These are ultimately sent to several
destinations. The system skill receives out of band messages ('stop', 'start', 'pause', 'resume', etc).
The fallback skill receives messages that don't match an intent and an individual skill may receive a
message from the intent service if an intent match is detected.

-------------
Channel Focus
-------------
The system manages the synchronization of resources between skills. The speaker is considered the output
channel while the microphone is considered the input channel and the assumption is there will be contention 
among multiple skills for these resources whose access must be serialized.

This is all handled in the base skill code (*pvx_base.py*) and the skill developer does not need to worry
about this as it all happens in the skill base class automagically. 

The skill base class relies on the system skill to accomplish this using 'request_focus' messages. The 
system skill manages access to these resources as descibed in the following section.

------------------
Skill Interactions
------------------
All skills fall into one of four categories

+ system
+ user
+ qna
+ media

The system skill makes the focus determination based on the categories of
the skills involved. This happens in the file 'skills/system_skills/skill_system.py'
in the method named 'output_focus_determination()'. 

.. code-block:: python

   if last_active_skill_category == 'media':
       # media skills are paused by everything
       # except a new media request which will
       # terminate the previous media skill
       if new_skill_cat == 'media':
           return 'cancel'
       else:
           return 'pause'

   if last_active_skill_category == 'qna':
       # qna skills are paused by everything except
       # media skills which terminate them
       if new_skill_cat == 'media':
           return 'cancel'
       else:
           return 'pause'

   if last_active_skill_category == 'user':
       if new_skill_cat == 'system':
           return 'pause'
       return 'cancel'

   return 'deny'

----------------------
Out of Band Processing
----------------------
An out of band message is a message which requires processing outside the normal
process flow. For example, if the user says "stop" this is considered a meta input
and it requires special processing rather than just sending it to the currently 
active skill. 

Out of Band (OOB) messages are produced by the intent service and sent to the system skill.
The system skill uses its overall knowledge of which skills are currently active, 
waiting on input, etc. to determine what to do with the OOB message. 

The system skill also allows other skills to register to receive out of band messages and
they may even create and register for new ones, so for example if a skill wanted to receive
all user input that started with 'halt foo', it could register 'halt foo' with the system
skill as an out of band and it will receive a message when that utterance is recognized.

----------------------
Skill Input Processing
----------------------
When a skill requests user input this translates to a request to the system skill to acquire
input channel focus. The way the system handles this is it sends the next raw input it 
receives to the skill. It shoudl be noted this happens **after** the normal process flow.

This means even though the skill currently in control of the input channel ultimately
receives the raw input, the input still goes though the normal audio input process which 
attempts to intent, handle OOBs, etc.

A side effect of this, is if a skill is waiting for a user input which might be the word 
stop (for example, "tell me user should i stop or start"), it will receive a 'stop' message
**before** it receives the user utterance. It is up to the skill to handle this edge case
which is easily accomplished with a stateful variable. 

-------
The HAL
-------
The system requires two audio components to be operational. A microphone for user input
and a speaker for user output. A headset works best and the system does not handle poor
AEC or other audio issues very well. As a result, it is recommended it is run on an 
adequate system. The :ref:`Installation` section describes how to determine this.

The directory 'framework/hal' contains all the code that is system/environment specific.
From a high level the system only needs to know how to change the volume, however, it also
allows for an initialization call and similar functionality for the microphone. As a result
the hal.cfg file contains an object for each environment. This object contains the command
to initialize the audio system if necessary (in most cases not needed), to get and set the
volume and to get and set the microphone level. 

The system relies on the 'amixer' command to accomplish these functions and
as a result, determining the 'amixer' channel names bcomes the issue for systems which do 
not work out of the box using the default values. 

For example, here is how the system sets the speaker volume on one linux system. 

.. code-block:: bash

   amixer sset Playback 20%

Most issues will arise from knowing the proper values to set for playback and record. The
'test/' directory contains two scripts to help with this issue. 

+ find_volume_control.py
+ list_input_devices.py

See 'framework/hal/README' for additional information.

---------------
The Message Bus
---------------
The message bus is a simple **web socket server** and associated client related code. It may be
found in the 'bus/' directory and provides a bridging mechanism to support both synchronous
and asynchronous operation. By default skills are assumed to be asyncio clients and behave in
a manner consistent with the Python asyncio protocol. Asyncio is a typical voluntary ELOS (enormous 
loop operating system), ala MS Windows which relies on the concept of a well-behaved program. 

A by-product of this is that non-well-behaved programs can starve themselves off of input messages
and render themselves inoperable.

Asyncio is an acquired taste and can present a daunting challenge to an entry level Python programmer. 

To mitigate this, the system provides a skill with the ability to identify itself as a synchronous skill.
Synchronous skills uses the methods 'sync_speak' and 'sync_listen' rather than their async counterparts.

Synchronous skills must set their *sync* flag to True in their super constructor like this

.. code-block:: python

   def __init__(self, bus=None, timeout=5):
       self.skill_id = 'my_skill'
       super().__init__(skill_id=self.skill_id, skill_category='user', sync=True)


The message bus is a targeted bus and messages are not broadcast to all endpoints. The downside to
this is a system monitor which could see all messages, even those not destined for it, and so this 
is accomplished in the socket server by sending out all messages to the special endpoint named 
'system_monitor'. 


