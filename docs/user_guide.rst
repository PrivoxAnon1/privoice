User's Guide
************

.. toctree::
   :maxdepth: 3

=======
Running
=======
To run PriVoice enter the following command 

.. code-block:: bash

   ./scripts/privoice_start.sh


If you would like to view the log files in real time run 

.. code-block:: bash

   tail -f tmp/logs/*

To stop the PriVoice voice assistant type 

.. code-block:: bash

   ./scripts/privoice_stop.sh

Note - you may have to hit Ctl+C first if you tail'ed the log files
as shown above.

=================
General Operation
=================
PriVoice is what is known as a 'wake word activated' voice 
assistant. This means it listens to everything but only attempts
to interpret an utterance if it is preceeded by the wake word. 

A 'wake word' is a word (or words) which, when recognized by the system
causes it to enter the 'active' state. You may say the wake word as
part of the sentnece 

*hey computer what time is it*


Or you may say the wake word by itself 

*hey computer*

In which case it will beep at you and then attempt to execute the next utterance it hears. In other words 

*hey computer*

<<Brief Delay>>

*what time is it*

The system also has the concept of an out of band (OOB) command. For example
'stop' is considered an out of band statement and is normally handled by the
system as expected (stop the currently active skill) as well as 'pause' and 
'resume' having the expected behavior.

*hey computer stop*

or

*hey computer*

<<Brief Delay>>

*stop*

===============
Common Commands
===============
The following commands assume you say the wake word followed by the command. 
The documentation will often use the following convention when describing commands ...

WW what time is it.

Which simply means you spoke the wake word (WW) first. Note you control what the 
wake word is by modifying the value in the *yava.yml* file. See :ref:`Configuration` for more 
information on how to change the wake word. The system ships with six skills installed by default. 

+ time and date skill
+ volume skill
+ weather skill
+ wiki skill
+ radio skill
+ example skill

Typical usage might be 

+ WW what time is it
+ WW what is today's date
+ WW <<brief delay>> set the volume to ninety percent
+ WW what is the volume set to
+ WW what is the weather forecast
+ WW who was Abraham Lincoln
+ WW play smooth jazz
+ WW run example one

Note the out of band phrases like 'stop', 'pause', 'resume' are often handled 
better by saying the wake word in isolation, then after the beep, speaking the command.
For example

WW <<brief delay>> stop

==================
System Information
==================
By default, the system operates in offline mode. If
it should happen to have an internet connection and if
it should happen to have a skill installed which uses
the internet, that will work as well.

The **skill manager** controls the installation and
removal of skills and supports the following spoken commands ...

+ install skill
+ delete skill
+ show active skills
+ show installed skills
+ show available skills
+ help skills
+ help skill manager

PriVoice consists of *services*, *system skills* and *user skills*. 
Users may install new skills or remove existing skills using either the 
skill manager or the command line. The :ref:`Skills` page shows how to
easily create new skills and add repositories to the system.

=================
PriVoice Services
=================
+ Speech Recognizer (STT) converts audio in to text
+ Intent Handler converts text to intents and dispatches skills
+ Text to Speech (TTS) provides ability to play a text string
+ Media allows playing  mp3 or wav data
+ Skill Manager manages skill installation and removal using voice

=====================
Default System Skills
=====================
+ system skill
+ volume skill
+ fallback skill
+ media skill
+ alarm skill

=====================
Default User Skills
=====================
+ time and date skill
+ example skill
+ weather skill(i)
+ wiki skill(i)
+ radio skill(i)

Note: i = requires internet connection

