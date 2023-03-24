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
+ WW     - wake word detected (computer)
  just the wake word, not the WW + utt, that is msg Q_UTT

It should be noted this code is triggered by a RAW message and it does not repeat this message.
This code is basically a simple stateful stream parser designed to handle the concept of a 
wake word (which can time out) and out of band (OOB) utterances.

Out of band processing is handled by the system skill and is described in more detail on
the :doc:`Developer Guide </developer>` page.

A *qualified utterance* (Q_UTT) is an utterance which is either preceeded by the wake word (or wake 
word phrase) or was received while the interpreter was in the *activated* state. The activated
state is a period of time from when the user speaks the wake word in isolation, to when the 
time-out period is reached. All of these parameters are available in the **yava.yml** configuration
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

===============
Shallow Parsing
===============
Extract information from utterances using shallow parsing.
This approach takes a sample sentence set and creates a
set of grammatical rules from them along with skeleton
methods and associated "rule to method" mapping dictionary.

-----
Usage
-----
1. Manually create sample sentences in file "sentences.txt" (or any file name you prefer).
2. Run cmu_parse.py sentences_filename.txt which will convert input file to "cmu_trees.txt"
3. Run produce_rules.py which creates a "grammar to method" map in file named "generated_parse_handlers.py".
4. Manually fill in the empty methods in file "generated_parse_handlers.py". This file was created by step (3). When done rename this to command_rule_handlers.py or question_rule_handlers.py accordingly.
5. In your code include parse_sentence from the file named "parse_sentence.py"


Example:
  from parse_sentence import parse_sentence

  info = parse_sentence("turn off the kitchen light")

Note the file 'generated_file_handlers.py' is created by the produce_rules.py script.
The file user_generated_handlers.py are the actual handlers which are created by the user.
In this case they are the default handlers provided by the system. You can use them or
replace them with your own if you prefer or add to them.


--------
Overview
--------
Shallow parsing is based on the concept that for our simple use-case we can
divide sentences into one of three categories; question, command or information.

If we take the command category only we can then break each sentence down into its
grammatical structure (a parse tree) and then flatten it into a grammatical rule.

This grammatical rule is known as a semi lexical structure (SLS) because it is 
devoid of its depth, however, it still contains some essence of the original 
lexical structure.

We then use this rule to invoke a specific method designed to handle just
sentences of this grammatical structure. 

The system may be considered *consistent* and  *complete* if only 
recognized *shallow patterns* are provided as input. For simple command and
query domains like a voice assistant there are typically less than 100-200 such 
unique patterns (there are only so many ways to say 'turn on the light')
and so the entire set may enumerated. For larger domains the system can 
recognize a new unrecognized pattern and learn it in real-time given a proper
feedback mechanism. 

Alternatively, the unrecognized utterance may be added to the training set and 
the new *mini parser* may be manually added.

The complete process looks like this ...


.. code-block:: bash

  STEP1) sentence ---> parse tree
  STEP2) parse tree ---> grammar rule
  STEP3) grammar rule ---> grammar rule handler

---------------
For example ...
---------------

.. code-block:: bash

  STEP1) sentence ---> parse tree
  close the living room window
  (VP close (NP the living room window))

  STEP2) parse tree ---> grammar rule
  (VP close (NP the living room window))
  VP NP

  STEP3) grammar rule ---> grammar rule handler
  VP NP
  resp = rule_map['VP_NP']

This will determine the sentence structure
then invoke the proper handler based on
the derived grammar rule. It is a very simple
pattern matching approach.

This is used only for imperatives and the skeleton is
generated but then modified manually ultimately producing
the command_rule_handlers.py file which is the actual code
that handles each unique command rule structure. this file
also includes the dictionary which is used as a branch
table for the various handlers.

If you run into command sentences that are not recognized
you can create the rule manually and then add your handler
to this file or you can create a text file of example command
sentences and run cmu_parse.py against them which will produce
a file named cmu_trees.txt which can then be fed into the file
named produce_rules.py which will convert them into an execuatble
python file named generated_rule_handlers.py. this is a raw
initial rule handler file which you can modify accordingly.
Typically you will sumply add your new rule handlers to this
file and keep the existing code.

The actual rule maps look like this ...


.. code-block:: bash

  def VP_NP_PP_NP_NP_NP_VP_NP(sentence):return vp_np_pp_np_np_np_vp_np(sentence)
  def VP_PP_NP_PP_NP_PP_NP(sentence):return vp_pp_np_pp_np_pp_np(sentence)
  def VP_NP_PP_NP_NP_NP_VP(sentence):return vp_np_pp_np_np_np_vp(sentence)
  def VP_NP_PRT_PP_NP(sentence):return vp_np_prt_pp_np(sentence)
  def VP_PRT_NP(sentence):return vp_prt_np(sentence)
  def VP_NP_PP_NP_ADJP_NP(sentence):return vp_np_pp_np_adjp_np(sentence)
  def VP_NP_NP_PP_NP_PRT(sentence):return vp_np_np_pp_np_prt(sentence)
  def VP_NP_PP_NP_NP_NP(sentence):return {'error':'unimplemented = VP_NP_PP_NP_NP_NP'}
  def VP_PP_NP_NP_PP_NP(sentence):return {'error':'unimplemented = VP_PP_NP_NP_PP_NP'}
  def VP_NP_NP_VP_PP_NP(sentence):return {'error':'unimplemented = VP_NP_NP_VP_PP_NP'}
  def VP_NP_PP_NP_PP_NP(sentence):return vp_np_pp_np_pp_np(sentence)
  def VP_NP_PP_NP_NP(sentence):return vp_np_pp_np_np(sentence)
  def VP_PP_NP_PP_NP(sentence):return vp_pp_np_pp_np(sentence)
  def VP_NP_VP_VP_NP(sentence):return {'error':'unimplemented = VP_NP_VP_VP_NP'}
  def VP_NP_ADVP_NP(sentence):return vp_np_advp_np(sentence)
  def VP_NP_PP_NP(sentence):return vp_np_pp_np(sentence)
  def VP_PP_NP_NP(sentence):return vp_pp_np_np(sentence)
  def VP_NP_PRT(sentence):return vp_np_prt(sentence)
  def VP_PP_NP(sentence):return vp_pp_np(sentence)
  def VP_NP(sentence):return vp_np(sentence)

  rule_map = {
    'VP NP PP NP NP NP VP NP':VP_NP_PP_NP_NP_NP_VP_NP,
    'VP NP PP NP NP PP NP':VP_NP_PP_NP_NP_PP_NP,
    'VP PP NP PP NP PP NP':VP_PP_NP_PP_NP_PP_NP,
    'VP NP PP NP NP NP VP':VP_NP_PP_NP_NP_NP_VP,
    'VP NP NP PP NP PRT':VP_NP_NP_PP_NP_PRT,
    'VP NP PP NP ADJP NP':VP_NP_PP_NP_ADJP_NP,
    'NP VP PP NP PP NP':NP_VP_PP_NP_PP_NP,
    'VP NP PP NP NP NP':VP_NP_PP_NP_NP_NP,
    'VP PP NP NP PP NP':VP_PP_NP_NP_PP_NP,
    'VP NP NP VP PP NP':VP_NP_NP_VP_PP_NP,
    'VP NP PP NP PP NP':VP_NP_PP_NP_PP_NP,
    'VP NP PP NP NP':VP_NP_PP_NP_NP,
    'VP PP NP PP NP':VP_PP_NP_PP_NP,
    'VP NP PRT PP NP':VP_NP_PRT_PP_NP,
    'VP NP VP VP NP':VP_NP_VP_VP_NP,
    'VP NP ADVP NP':VP_NP_ADVP_NP,
    'VP NP PP NP':VP_NP_PP_NP,
    'VP  PP NP NP':VP_PP_NP_NP,
    'NP VP NP PRT':NP_VP_NP_PRT,
    'NP VP PP NP':NP_VP_PP_NP,
    'VP NP PRT':VP_NP_PRT,
    'VP PP NP':VP_PP_NP,
    'NP VP NP':NP_VP_NP,
    'VP PRT NP':VP_PRT_NP,
    'VP NP':VP_NP,
  }

The methods are small parsers. Here is the handler for the shallow token pattern "VP PRT NP".

.. code-block:: python
   :linenos:

    def vp_prt_np(node):
      #(VP turn (PRT up) (NP the heat))
      verb = get_tag_value(VP_TAG, node)
      value = get_tag_value(PRT_TAG, node)
      subject = get_tag_value(NP_TAG, node)
      subject_pp = ''
      return {'error':'', 'verb':verb, 'value':value, 'subject':subject, 'squal':subject_pp}

