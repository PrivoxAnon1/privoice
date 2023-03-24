Skills
******

.. toctree::
   :maxdepth: 2

.. _skills:

===============
Creating Skills
===============
PriVoice skills are simple Python programs that run in their own 
virtual environment using their own Python interpreter. This level
of isolation ensures skills don't interfere with each other. 

If skills need to communicate they should do so using the message
bus. The message bus is a simple websocket server and the send_msg()
command is built into all PriVoice skills.

Skills typically respond to spoken questions or commands. All skills
have a **register_intent()** method and a **bus.on()** method which
allows them to link an incoming message to a method. By default skills
are asynchronous, however, facilities exist to run skills in a synchronous 
manner.

-----------
Hello World
-----------
Open your terminal and change into the skills/user_skills directory. 
Create a new directory named privoice_hello and then change into that 
new directory.

.. code-block:: bash

   cd skills/user_skills
   mkdir privoice_hello
   cd privoice_hello

Create a file named skill.json. It should look like this ...

.. code-block:: bash


   {
	"skill_id":"hello_skill",
	"name":"hello skill",
	"requires_internet": "no",
	"description":"Hello World skill.",
	"search_terms":["hello", "hi"]
   }   

Next, create a file named init.py and put this in it ...

.. code-block:: python
   :linenos:

   from skills.pvx_base import PriVoice
   from threading import Event

   class HelloSkill(PriVoice):
       def __init__(self, bus=None, timeout=5):
           super().__init__(skill_id='hello_skill', skill_category='user')
           self.speak("Hello World.")

       def stop(self, msg):
           #print("\n*** Do nothing stop hit ***\n")
           pass

   if __name__ == '__main__':
       hs = HelloSkill()
       Event().wait()  # Wait forever

Now change back to the base PriVoice directory

.. code-block:: bash

   cd ../../..

Stop PriVoice if it was previously running.

.. code-block:: bash

   ./scripts/privoice_stop.sh

and restart it so it picks up your new skill.

.. code-block:: bash

   ./scripts/privoice_start.sh

You should hear your skill say "hello world" when it is loaded.

This works because when PriVoice first starts it scans the "skills/user_skills/" directory
looking for directories that start with **privoice_**. If it finds one it then looks for a
**skill.json** file and an **__init__.py** file and if it finds those two files in the subdirectory
it assumes it has found a skill and it will attempt to start it by sourcing its virtual environment
and then executing the "__init__.py" file in the background. This is why when you restarted 
PriVoice it automatically found your skill and executed it. 

**All skills must have a unique skill ID**.
Notice line 6 in the output above. It is calling the base class constructor. This is 
where you establish your skill's ID. The skill ID must be unique across the system. 
It is how the message bus knows who to deliver a message to. In our example above,
we used the skill ID 'hello_skill' as shown again, below 

.. code-block:: bash

   super().__init__(skill_id='hello_skill', skill_category='user')


Your skill will receive any messages destined for the target skill ID 'hello_skill'.
Typically, your skill will respond to messages that are sent to it. For example, when you
register an intent (`register_intent()`_) you are telling the system to call a method you 
provide when a noun/verb match you specified is recognized.

Obviously this is a contrived example but it demonstrates how 
simple it is to create and deploy a new skill.

In the next section we will create a local skill repository which 
is just a directory that contains skills, and we will use the built 
in skill manager to install and run our skills from this repository.

Keep in mind, if you just want to add a new skill to the system without going
through the skill manager and setting up a repository, you can simply add the 
new skill directory under the "skills/user_skills/" directory as described above 
and it will work as expected.

---------------------------
Creating a Local Repository
---------------------------
Open your terminal and create a directory somewhere on your file system. 
For example

.. code-block:: bash

   $ pwd
   /home/anon1

   $ mkdir my_repo
   $ cd my_repo
   $ pwd 
   /home/anon1/my_repo

Later we will add this local repository to our configuration file.

This is our new local repository. We will put our new skills in here. 
To create a new skill ...


.. code-block:: bash

   $ mkdir privoice_my_skill
   $ cd privoice_my_skill

Now create a file named skill.json. It should look like this ...

.. code-block:: bash


   {
	"skill_id":"my_skill",
	"name":"my skill",
	"requires_internet": "no",
	"description":"My first skill.",
	"search_terms":["my", "mine", "me"]
   }


Finally, create a file named init.py and put this in it ...

.. code-block:: bash


   from skills.pvx_base import PriVoice
   from threading import Event

   class MySkill(PriVoice):
       def __init__(self, bus=None, timeout=5):
           super().__init__(skill_id='my_skill', skill_category='user')

           self.register_intent('Q', 'what', 'my skill', self.handle_what)
           self.register_intent('Q', 'who', 'my skill', self.handle_who)
           self.register_intent('C', 'help', 'my skill', self.handle_help)

       def handle_who(self, msg):
           self.speak("I am my skill.")

       def handle_what(self, msg):
           self.speak("My skill is my first skill.")

       def handle_help(self, msg):
           self.speak("You asked for help with my skill.")

       def stop(self, msg):
           #print("\n*** Do nothing stop hit ***\n")
           pass

   if __name__ == '__main__':
       ms = MySkill()
       Event().wait()  # Wait forever

Finally, add the new repository to the skill manager repositories json file. 
It is located in framework/services/skill_mamager/repositories.json.

Edit this file to point to your new repository. Change the values MYHOME and MYREPO

.. code-block:: bash


   [

   { "repo_name":"Privox Approved Skills", "repo_uri":"https://github.com/PrivoxAnon1/privox.git", "repo_description":"Privox provided skills" },

   { "repo_name":"Local Skills", "repo_uri":"/home/MYHOME/MYREPO/", "repo_description":"User provided local skills" }

   ]

The next time you restart the system it will pick up your repo and you can use the skill manager to install and run your skills.


-------------
Skill Intents
-------------
An intent is the matching of an endpoint (a method in the skill) with a sentence type, sentence subject and a sentence verb. 


.. code-block:: python

    self.register_intent('C', 'turn', 'light', self.handle_change_light)


Which says call my method named *handle_change_light* when the sentence subject is *light* and the sentence verb is *turn*. 

---------
Ailiasing
---------
In many cases, the utterances 

+ Turn off the light
+ Turn the light off
+ Shut off the light 
+ Change the light to off
+ Set the light off

Could all call the same method. This method could be called the **alter** method where the action *alter* can be used as an alias for the above verbs 'Turn', 'Shut', 'Change' and 'Set'. 


It is often convenient to alias both the subject and verb. For example, regardless of whether the user says 'shut the light' or 'turn off the light' or 'set the light on' in all cases we really just want to call the same method (assuming it can easily derive the value) which will ultimately alter the value of the light. This compressing of multiple aliases into a single endpoint is known as *implicit aliasing* as opposed to *explicit aliasing* which is simply the mapping of multiple verbs (or subjects) to a single root verb (or subject). 

This code snippet from the volume skill demonstrates implicit aliasing of both a set of nouns and a set of verbs.


.. code-block:: python

    verbs = ['set', 'change', 'modify']
    subjects = ['microphone', 'mic', 'input']

    for subject in subjects:
        for command in verbs:
            self.register_intent('C', command, subject, self.handle_change_mic)


Any combination of subject and verb will ultimately lead to the *handle_change_mic* method being called.

===============
Skill Operation
===============
Typically a skill registers one or more intents and then waits for the user to utter something that matches the intent. 
Intents come in two basic types; commands or queries. In other words the system expects you to either ask it a question 
or give it a command. It does not currently know what to do with idle chatter and/or gossip and will tend to ignore this sort of input.

As a result, an intent is defined as a sentence type (command or question) and a subject and a verb. For example

Shut the door (subject = door, verb = Shut, type = command)

What time is it? (subject = time, verb = what, type = question)

When your skill is first loaded it registers any intents it may want to respond to and then it goes away and waits
to be called. To have your method named 'handle_close()' invoked when someone says "shut the door" we would register the following intent

.. code-block:: bash

   self.register_intent('C', 'shut', 'door', self.handle_close)

And the code for 'handle_close' should look something like this 

.. code-block:: bash

       def handle_close(self, msg):
           self.speak("You asked to close the door.")

Now, when someone says "shut the door" your "handle_close" method will be called with the message. This message
contains information related to the actual sentence spoken by the user.

For example, when the user says "WW what time is it" the "privoice_timedate" skill will be called with the following message

.. code-block:: bash

  {'msg_type': 'utterance', 
  'source': 'intent_service', 
  'target': 'time_skill', 
  'data': 
    {'utt': 
      {'error': '', 
      'sentence_type': 'Q', 
      'sentence': 'what time is it?', 
      'normalized_sentence': 'what time is it?', 
      'qtype': 'qt_wh', 
      'np': 'time', 
      'vp': 'is', 
      'subject': 'time', 
      'squal': '', 
      'question': 'what', 
      'qword': 'what', 
      'value': '', 
      'raw_input': 'computer what time is it?', 
      'verb': 'is', 
      'aux_verb': 'time', 
      'rule': 'VP NP', 
      'tree': 'what time (VP is (NP it)) ?', 
      'subtype': '', 
      'from_skill_id': '', 
      'skill_id': 'time_skill', 
      'intent_match': 'Q:time:what'}, 
      'subtype': 'utt'
    }, 
  'ts': '2023-03-21 14:06:22'}

The skill does not need to do anything with the message. It is provided as input and the skill may use it or ignore it.

=========
Skill API
=========
The example skill located in the *skills/user_skills/privoice_example* directory is a good example
of how a basic skill can communicate with the user. The time and date (*skills/user_skills/privoice_timedate*) skill
is an example of a minimalistic user skill. These are good skills to use as a template for
creating a new skill. 

All skills that inherit from the PriVoice class have the following built-in methods available to them.

-------
speak()
-------
The speak call is used to convert a text string to wav data and then play the wav data on the audio output channel. 
The system will handle chunking and other system related functions like 'pause', 'resume', etc.
Note the speak call is a non blocking call so your skill will regain control immediately, **before** the actual audio has **completed** playing!
If you call speak again without waiting until the callback is called you will interrupt yourself which is probably **not** what you want.
To avoid this use the callback, or use the *sync_speak()* call described below.


.. code-block:: python

   speak(text, wait_callback, engine, model, voice)

   # required
   text - text string to speak

   # optional
   wait_callback - method to call when speak has completed
   engine - currently ignored
   model - the TTS model to use
   voice - the TTS voice to use

**Examples:**

.. code-block:: python

   self.speak("Hello Joe")
   self.speak(txt, wait_callback=my_callback, voice="p270")

------------
sync_speak()
------------
The sync speak call is used to convert a text string to wav data and then play the wav data on the audio output channel. 
The system will handle chunking and other system related functions like 'pause', 'resume', etc.
The sync_speak call is a blocking call so your skill will be suspended until either the call completes or it times out. 
The return value indicates whether the call actually completed (return value is True) or if it timed out (returns False).
You must set the sync flag in the super constructor of your skill to True if you use this method..

.. code-block:: python

   sync_speak(text, wait_callback, engine, model, voice)

   # required
   text - text string to speak

   # optional
   engine - currently ignored
   model - the TTS model to use
   voice - the TTS voice to use

**Examples:**

.. code-block:: python

   text = "Who stole the cookies from the cookie jar?"

   # speak using default voice
   self.sync_speak(text)

   # speak using different voice
   self.sync_speak(text, voice="p270")

   # speak using different voice and model
   self.sync_speak(text, model="tts_models/en/vctk/vits", voice="p270")

------------
play_media()
------------
The play_media call plays a media file.

.. code-block:: python

   play_media(file, delete_on_complete, media_type)

   # required
   file - the file to play.

   # optional
   delete_on_complete - if True will delete the file after it has been played
   media_type - 'wav', 'mp3', or 'stream_vlc'

**Examples:**

.. code-block:: python

   self.play_media(uri, False, 'stream_vlc')

----------------
get_user_input()
----------------
The get_user_input call waits for a user utterance and either calls the user
provided callback method with the user input, or it calls the user supplied
timeout method if a timeout occurs. 

.. code-block:: python

   get_user_input(callback, prompt, timeout_callback)

   # required
   callback - the method to call with the user utterance.

   # optional
   prompt - if present will be spoken first
   timeout_callback - if provided will be called if a timeout is reached

**Examples:**

.. code-block:: python

   self.get_user_input( self.handle_user_input,
                        "Who are you?",
                        self.handle_user_input_timeout )


-----------------------
get_user_confirmation()
-----------------------
The get_user_confirmation call is a special case of the 
get_user_input call. When the user callback is invoked it is provided with
either the string 'yes' or the string 'no' based on the user's response. 

.. code-block:: python

   get_user_confirmation(callback, prompt, timeout_callback)

   # required
   callback - the method to call with the user utterance.

   # optional
   prompt - if present will be spoken first
   timeout_callback - if provided will be called if a timeout is reached

**Examples:**

.. code-block:: python

   self.get_user_fonfirmation( self.handle_user_input,
                        "Confirm you want to do bla.",
                        self.handle_user_input_timeout )


--------------
send_message()
--------------
Sends a **'skill'** message on the bus to the target skill id. Note, message must be a dict.

.. code-block:: python

   send_message(target, message)

   # required
   target - the endpoint target bus identifier. also known as a skill id.
   message - a dict to be sent on the bus.


**Examples:**

.. code-block:: python

   message = {'subtype':'arbitrary_value',
              'skill_data':'testing one two three'}
   self.send_message('some_skill', message)

   self.send_message('some_skill', {'test':'123'})


-----------------
register_intent()
-----------------
Bind a sentence type, subject and verb to a callback.
Ultimately sends a message on the bus to the intent service.

.. code-block:: python
   
   register_intent(intent_type, verb, subject, callback):

   # required
   intent_type - 'C' for command or 'Q' for question
   verb - the verb to match
   subject - the subject to match
   callback - method to be called on an intent match


**Examples:**

.. code-block:: python

   class TimeSkill(PriVoice):
       def __init__(self, bus=None, timeout=5):
           super().__init__(skill_id='time_skill', skill_category='system')

           self.register_intent('Q', 'what', 'time', self.handle_time_match)
           self.register_intent('Q', 'what', 'date', self.handle_date_match)
           self.register_intent('Q', 'what', 'today', self.handle_date_match)
           self.register_intent('Q', 'what', 'day', self.handle_day_match)


-------------
sync_listen()
-------------
Wait for user input. Returns a string representing the user's utterance, or an
empty string on a timeout. 

.. code-block:: python
   
   sync_listen()

   # optional
   prompt - if present will be played first


**Examples:**

.. code-block:: python

   user_input = self.sync_listen()

   user_input = self.sync_listen("Who are you?")

   say = "Say hello"
   user_input = self.sync_listen(say)


Note: you must set the sync flag in the super constructor to True if you use either of the "sync" methods (sync_speak and sync_listen).

==========
Q&A Skills
==========
Q&A skills are skills which respond to questions that do not match an intent. 
For example, the question "Who was Abraham Lincoln" will not match any intent
and it will fall through to the fallback skill which will send out a request to all
registered Q&A skills to see which one will ultimately handle the request.

This decision will be based on the confidence level the skill sends back to
the fallback skill when it sends out the question. The fallback skill will 
award the work to the skill which responded with the highest confidence level.

Q&A Skills additionally have to implement ...

.. code-block:: bash

   def get_qna_confidence( msg )
   And
   def qna_answer_question( msg )

get_qna_confidence takes in a question and responds with the confidence 
level the skill believes has in its ability to answer the question.

qna_answer_question takes in the question and produces the output. It is 
called when the Q&A skill is selected by the fallback skill to answer the
question. This message is only sent to the Q&A skill which responded with
the highest confidence level. 

This is how the system resolves contention among multiple skills which can 
answer open ended questions like wiki, duck duck go, etc.

See the wiki skill source code for an example of a Q&A skill.

============
Media Skills
============
Media skills are skills which play some form of media like a wav or mp3 file
or stream, or even a video. 

The system media skill acts as an arbitrer much like the fallback skill does with 
the Q&A skills, and gathers confidence levels from registered media skills when a 
media type command (play, listen, etc) is recognized.

The ultimate play message is only sent to the media skill which responded with
the highest confidence level.

Skills which inherit from the Media skill have to implement these additional methods 

.. code-block:: bash

   def get_media_confidence( msg )
   And
   def media_play( msg )


See the radio skill source code for an example of a media skill.

