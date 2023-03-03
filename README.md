#PriVoice - a privacy respecting voice assistant

Installation
------------

./scripts/linux_install.sh


Verify Installation
-------------------

. ./scripts/init_env.sh

# yes, that's dot space dot slash.

cd test/voice

./recognizer.sh

You should see what you say printed on the screen.
If not <a href='#'>click here</a> to figure out why.



Running PriVoice
----------------

The first thing you should always do is to change into the base directory and run

. ./scripts/init_env.sh

this will ensure you have activated the proper virtual environment so all scripts will run correctly. 


Everything runs from this base directory. For example, 

python bus/MsgBus.py 

or

python skills/user_skills/privoice_myskill/__init__.py


To start and stop PriVoice proper run ...


./scripts/privoice_start.sh

or 

./scripts/privoice_stop.sh


To run individual skills (for example) ...


./scrips/run_skill skills/user_skills/privoice_myskill


The Hello World Skill
=====================

Open your terminal and change into the skills/user_skills directory. Create a new directory named privoice_hello and then change into that new directory.

cd skills/user_skills

mkdir privoice_hello

cd privoice_hello


Create a file named skill.json. It should look like this ...

{
	"skill_id":"hello_skill",
	"name":"hello skill",
	"requires_internet": "no",
	"description":"Hello World skill.",
	"search_terms":["hello", "hi"]
}


Finally, create a file named __init__.py and put this in it ...

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

cd ../../..


Stop PriVoice if it was previously running.

./scripts/privoice_stop.sh

and restart it so it picks up your new skill.

./scripts/privoice_stop.sh

You should hear your skill say "hello world" when it is loaded.

Obviously this is a contrived example but it demonstrates how simple it is to create and deploy a new skill. 

In the next section we will create a local skill repository which is just a directory that contains skills, and we will
use the built in skill manager to install and run our skills. 


Creating a local repository
===========================

Open your terminal and create a directory somewhere on your file system. For example 

$ pwd
/home/anon1

$ mkdir my_repo
$ cd my_repo

$ pwd
/home/anon1/my_repo

Later we will add this local repository to our configuration file. 

This is our new local repository. We will put our new skills in here. To create a new skill ...

$ mkdir privoice_my_skill

$ cd privoice_my_skill

Now create a file named skill.json. It should look like this ...

{
	"skill_id":"my_skill",
	"name":"my skill",
	"requires_internet": "no",
	"description":"My first skill.",
	"search_terms":["my", "mine", "me"]
}


Finally, create a file named __init__.py and put this in it ...


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



Skill Developer API
-------------------

The 'example1' skill located in the user_skills/ directory is a good example
of how a basic skill can communicate with the user. The time and date skill
is an example of a minimalistic user skill.

All skills that inherit from the PriVoice class have these methods available ...

+ speak(text, wait=callback)
+ play_media(file_uri, delete_on_complete='false')
+ converse(timeout)
+ get_user_input()
+ get_confirmation()
+ send_message(message)
+ register_intent(intent_type, verb, subject, callback)
+ sync_speak(text)
+ sync_listen(prompt)

Note: you must set the sync flag in the super constructor to True if you use either of the sync_ methods!

additionally, if a skill wishes to see all messages destined for it, it may
add the 'msg_handler' parameter in its super init call. See the help skill
for an example of this.


Q&A Skills additionally have to implement ...

    def get_qna_confidence( msg )

And

    def qna_answer_question( msg )


And skills which inherit from the Media skill have to implement these methods ...

    def get_media_confidence( msg )

And

    def media_play( msg )


Helpful Modules
---------------

The inflect module provides speakable numbers. It does things like converting

    Thursday April 27

to

    Thursday April twenty seventh


Which some may find helpful.

The Lingua Franca module provides advanced sentence parsing for things like
extracting dates and times from spoken words. For example

    '7 pm the day after tomorrow'

would return a datetime object. This can also be helpful when processing
spoken input.



Manifest
--------

+ bus - the system message bus

+ framework - system framework

+ __init__.py - empty

+ README.md - this file

+ scripts - various scripts to start and stop the system

+ skills - both user and system skills

+ test - test and benchmark code

+ tmp - temporary location to store various files. note logs files are here

+ venv_ia - if present, the virtual environment created during installation

+ yava.yml - system wide configuration file



Current Skills List
-------------------

+ alarm
+ connectivity
+ email
+ example1
+ ha_skill
+ help
+ npr_news
+ rfm
+ timedate
+ weather
+ wiki
+ youtube
+ local_wiki
+ local_music
+ duck_duck_go
+ wolfram_alpha



Design Notes
------------

1) By default skills are async and will block proper operation if they 
   loop on time.sleep(). To correct this if you are not comfortable with 
   async programming, set the sync flag in your super constructor to True

2) Converse - beware the word 'stop' if you need to handle it as input.


3) skills need to be internet presence aware. If they require an internet 
   connection they need to respond appropriately. the assumption is common 
   play and common query skills already do so.



