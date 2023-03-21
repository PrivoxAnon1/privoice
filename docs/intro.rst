Introduction
************

.. toctree::
   :maxdepth: 2

--------
Overview
--------
PriVoice is a full featured, privacy respecting, open source voice assistant.
It is comparable to products like Alexa and Suri with several key differences.

+ Runs locally with no network connection required.
+ Privacy respecting, secure operation. No data leaves your system.
+ NLP (Noun/Verb) intent matching.
+ Unrestricted use of user contributed skills.
+ Unlimited skill stackability. Hyper-link based VUI.

Current constraints on quality STT like poor echo cancellation, CPU processing power, GPU/TPUs (or lack thereof) and RAM (not enough) will eventually disappear at which point a fully functional, completely local, privacy respecting voice framework will become the norm. PriVoice is not designed for inferior hardware and if you run it on low end systems you will most likely be disappointed. That being said, most laptops or desktops with a headset or decent mic/speaker combination can run PriVoice with no issues.

PriVoice was created to address the limitations inherrent in most existing voice frameworks. Issues arising from skill interractions, channel focus, out of band recognition, barge-in and skill isolation are of no concern to the PriVoice skill developer. The skill developer is free to assume this all just works as it is supposed to and is free to concentrate on whatever the skill is supposed to do.

PriVoice runs STT and TTS locally and does not send any data outside of your device. This is true unless you choose to use a skill which requires internet access (like the wiki skill or the weather skill which are installed by default) in which case requests are made to those sites but no information other than the query is shared. Even this behavior may be disabled by simply removing the following skills from the default installation, in which case the device will operate completely locally with no internet connection required.

--------------------------------
Skills Which Access the Internet
--------------------------------
+ wiki skill
+ radio skill
+ weather skill

One of the goals of PriVoice is to enable developers to create voice enabled applications without having to sacrifice their privacy, or the privacy of their users. There is no skill store or approval process. Some existing skills for PriVoice include

+ email skill
+ duck duck go skill
+ youtube skill
+ home assistant skill
+ npr news skill

