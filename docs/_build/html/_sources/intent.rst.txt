Intent Processing
*****************

.. toctree::
   :maxdepth: 2


.. _intent processing:

Intent processing is the process of matching up an *endpoint* with an input utterance.
An *input utterance* is the text produced by the speech to text (STT) process and is a 
result of what is provided to the audio input channel which in most cases is the microphone.

Input utterance messages are presented on the message bus as **raw** messages sent to the
intent service. The intent service forwards them onto the interpreter function. 
The interpreter takes in raw text messages and converts them to one of four message types

+ Q_OOB  - qualified out of band (example - computer stop)
+ U_OOB  - unqualified out of band (example - stop)
+ Q_UTT  - qualified utterance (computer what time is it)
+ WW     - wake word detected (just the wake word, not the ww + utt, that is msg Q_UTT)

It should be noted this code is triggered by a RAW message and it does not repeat this message.
This code is basically a simple stateful stream parser designed to handle the concept of a 
wake word (which can time out) and out of band (OOB) utterances.

Out of band processing is handled by the system skill and is described in more detail on
the Developer page. 

A *qualified utterance* (Q_UTT) is an utterance which is either preceeded by the wake word (or wake 
word phrase) or was received while the interpreter was in the *activated* state. The activated
state is a period of time from when the user speaks the wake word in isolation, to when the 
time out period is reached. All of these parameters are available in the 'yava.yml' configuration
file in the base directory.

Qualified utterances are divided into one of three utterance types 

+ Question
+ Command
+ Informational

Informational utterances are ignored. Questions and commands are parsed using a natural language 
approach which produces among other things the recognized 'subject' and 'verb' if they exist. 

These are then used to determine if an *endpoint intent match* exists. If one exists, a message is sent
to the matched endpoint along with all known information about the utterance. If no intent is matched 
a message is sent to the endpoint registered on the message bus as the 'fallback skill'. 

=======
Intents
=======
It is possible to derive **intent** from *input utterances* in many different ways. For example, 
we could simply have a piece of code which looked like this in our intent processor 

.. code-block:: python

   if utterance.startswith('boo'):
       send_msg_to_boo(utterance)
   else:
       send_msg_to_hoo(utterance)

We could also use a regular expression to match an input utterance to an endpoint

.. code-block:: python

   if re.findall(r"boo", utterance):
       send_msg_to_boo(utterance)
   else:
       send_msg_to_hoo(utterance)

PriVoice uses the utterance **type**, the utterance **subject** and the utterance **verb** 
to match an input utterance to an endpoint. It does so by allowing endpoints to register 
intents (the combination of type, subject and verb) and when that intent is matched a message
is sent to the associated endpoint. 

It should be noted the intent service is a first come first serve service and it will reject
duplicate intent (also known as **intent clash**) registration requests.


