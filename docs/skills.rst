Creating Skills
***************

.. toctree::
   :maxdepth: 2

.. _skills:

======
Skills
======

PriVoice skills are simple Python programs that run in their own 
virtual environment using their own Python interpreter. This level
of isolation ensures skills don't interfere with each other. 

If skills need to communicate they should do so using the message
bus. The message bus is a simple websocket server and the send_msg()
command is built into all PriVoice skills.

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

Finally, create a file named init.py and put this in it ...

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

   ./scripts/privoice_stop.sh

You should hear your skill say "hello world" when it is loaded.

Obviously this is a contrived example but it demonstrates how 
simple it is to create and deploy a new skill.

In the next section we will create a local skill repository which 
is just a directory that contains skills, and we will use the built 
in skill manager to install and run our skills.

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

=========
Skill API
=========
The 'example1' skill located in the user_skills/ directory is a good example
of how a basic skill can communicate with the user. The time and date skill
is an example of a minimalistic user skill.

All skills that inherit from the PriVoice class have the following methods available to them.


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

