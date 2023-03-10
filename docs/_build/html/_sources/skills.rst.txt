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

All skills that inherit from the PriVoice class have the following methods available.

+ speak(text [, wait_callback, engine, model, voice])
+ play_media(file_uri [, delete_on_complete])
+ converse(timeout)
+ get_user_input()
+ get_confirmation()
+ send_message(message)
+ register_intent(intent_type, verb, subject, callback)
+ sync_speak(text [, wait_callback, engine, model, voice])
+ sync_listen(prompt)

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

===============
Advanced Topics
===============
+ Skill Categories
+ Changing the TTS Voice
+ Registering Intents
+ Getting User Input
+ The Message Bus
+ Synchronous Versus Asynchronous Skills

