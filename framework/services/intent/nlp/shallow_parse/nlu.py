# The goal is to produce a consistent structure
# for representing sentences, ala AMR.
# for me this is a class with two attributes;
# the sentence syntactical structure and the 
# sentence insight which includes things like
# command/verb, subject, value, etc
#
# For example:
#   turn the light in the living room on
#   turn on the light in the living room 
#   turn the living room light on
#
# Should all equal the same thing.
#
#  cmd=alter, value=on, subject=the living room light
# and other stuff like plurality and tense.
#
# note - 'the' is important. It's not 'any' or 'a', its a
# definate article which could convey additional meaning
# downstream so we capture it as well as tense and a 
# plural indicator.
#
# also note we do heavy verb aliasing so while
# the root cmd might be 'alter', this could be 
# derived from one of many aliases like turn, change
# modify, set, alter, etc. 
import re, os
from framework.services.intent.nlp.shallow_parse.parse_question import parse_question
#from framework.services.intent.nlp.remote.cmu_parse import remote_get_tree
from framework.services.intent.nlp.local.parse_interface import local_get_tree as lgt
from framework.util.utils import normalize_sentence

from framework.services.intent.nlp.shallow_parse.produce_rules import get_shallow_rule_from_tree
from framework.services.intent.nlp.shallow_parse.command_rule_handlers import rule_map as command_rule_map
from framework.services.intent.nlp.shallow_parse.concepts import concepts, command_concept_map
from framework.services.intent.nlp.shallow_parse.shallow_utils import (
        get_node, 
        get_nodes, 
        extract_proper_nouns,
        remove_articles,
)

##
# not sure if this belongs here or in the shallow parse dir
# try to determine if a sentence/utterance is a question

# note - 'which' and 'how' will need special handling
abs_qwords = ['is', 'does', 'do', 'did', 'are', 'can', 'who', 'would', 'which', 'how']

# if a sentence starts with one of these ...
qwords = ['have', 'or', 'could', 'would', 'should', 'when', 'where', 'why', 'whose', 'whom', 'why', 'is', 'does', 'do', 'did', 'are']

# it must be followed by one of these
aux_verbs = ['be', 'can', "can't", 'could', 'dare', 'do', 'have', 'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would', 'was', 'were']

def get_stype(sentence):
    sentence = sentence.lower()
    sentence_type = 'unknown'
    if len(sentence.split(" ")) > 2:
        # discard samples less than 2 words in length
        first_word = sentence.split(" ")[0].lower().strip()
        second_word = sentence.split(" ")[1].lower().strip()

        if first_word == 'will':
            # special case the word 'will'
            sentence_type = 'Q'
            if second_word == 'is' or second_word == 'can':
                # actually many just aux_verb
                sentence_type = 'I'

        # need special handling for 'what', also as in "what time is it"
        # versus "what you don't know can hurt you" to "what happens in
        # vegas stays in vegas". we are going to soon need to start
        # dealing with classes of words here and the exceptions to
        # those combinations rather than this edge case approach
        if first_word == 'what':
            # special case the word 'what'
            sentence_type = 'Q'
            if second_word == 'the':
                sentence_type = 'I'

        if sentence_type == 'unknown':
            # still don't know what type of sentence
            if first_word in abs_qwords:
                sentence_type = 'Q'
            else:
                if (sentence.find("?") > -1 or first_word in qwords and (second_word in qwords or second_word in aux_verbs)):
                    sentence_type = 'Q'
                else:
                    sentence_type = 'I'

    return sentence_type
##


class Insight:
  def __init__(self, sentence):
    self.proper_nouns = extract_proper_nouns(sentence)
    self.tense = 'present'
    self.plural = False
    self.verb = ''
    self.aux_verb = ''
    self.qtype = ''
    self.subject = ''
    self.squal = ''
    self.value = ''
    self.dependent = ''
    self.question = ''
    self.np = ''
    self.vp = ''
    self.concept = ''


class Structure:
  def __init__(self, sentence):
    self.original_tree = lgt(sentence)

    # strip off leading '(S ' and trailing ')'
    self.tree = self.original_tree[3:-1]
    self.nodes = get_nodes(self.tree)
    self.shallow = get_shallow_rule_from_tree(self.tree).strip()


class SentenceInfo:
  def __init__(self, base_dir):
    self.media_verbs = ['play', 'watch', 'listen']
    self.sentence_type = 'U'

    # create 'question words' list
    qw_file_name = 'question_words.txt'
    if base_dir is not None:
        qw_file_name = base_dir + '/framework/services/intent/nlp/shallow_parse/' + qw_file_name

    self.question_words = []
    fh = open(qw_file_name)
    for line in fh.readlines():
        line = line.strip()
        if len(line) > 1:
            self.question_words.append(line)
    fh.close()

  def handle_unknown_grammar(self, sentence):
    # eventually could give it one last generic try here
    self.sentence_type = 'U'
    return False

  def dump(self):
    print("utt = %s" % (self.original_sentence,))
    print("sentence type = %s" % (self.sentence_type,))
    print("qtype:%s" % (self.insight.qtype,))
    print("tree = %s" % (self.structure.tree,))
    print("spid = %s" % (self.structure.shallow,))
    print("nodes: (%s)" % (len(self.structure.nodes),))
    for node in self.structure.nodes:
        print("    %s" % (node,))
    print("proper nouns = %s" % (self.insight.proper_nouns,))
    print("qword:%s" % (self.insight.question,))
    print("qaux:%s" % (self.insight.aux_verb,))
    print("verb:%s" % (self.insight.verb,))
    print("value:%s" % (self.insight.value,))
    print("subject:%s" % (self.insight.subject,))

  def get_sentence_type(self, sentence):
    return get_stype(sentence)
    # for now basically question or Info
    # will refine further downstream
    vrb = sentence.split(" ")[0]
    resp = "I"   
    for wrd in self.question_words:
        if sentence.lower().startswith(wrd):
            resp = "Q"
            break
    return resp

  def handle_less_than_three_words(self, sentence):
        tmp_tree = self.structure.tree.replace("(VP ","")
        tmp_tree = tmp_tree.replace("(S ","")
        tmp_tree = tmp_tree.replace(")","")
        tmp_tree = tmp_tree.replace("  "," ")
        self.insight.verb = tmp_tree.strip()
        self.insight.subject = ''
        self.sentence_type = 'O'  # single word can only be an oob
        sa = tmp_tree.split(" ")
        if len(sa) > 1:
            # verb subject command recognized
            self.sentence_type = 'C'
            self.insight.verb = sa[0]
            self.insight.vp = self.insight.verb
            self.insight.subject = sa[1]
            self.insight.np = self.insight.subject

        return True

  def parse_utterance(self, sentence):
    self.original_sentence = sentence
    self.sentence_type = self.get_sentence_type(sentence)
    self.normalized_sentence = normalize_sentence(sentence)
    self.structure = Structure(self.normalized_sentence)
    self.insight = Insight(self.normalized_sentence)

    #print("PARSE_UTT: type=%s" % (self.sentence_type,))

    if self.structure.shallow == "VP" or (self.structure.shallow == "" and len(sentence.split(" ")) == 1):
      # if one or two word utterance handle it and bail
      return self.handle_less_than_three_words(sentence)

    start_verb = self.original_sentence.split(" ")[0].lower()

    if start_verb in self.media_verbs:
        # if a media sentence we are done for now
        # TODO do better than just 'starts with word'
        self.sentence_type = 'M'
        return True

    # if question parse differently 
    if self.sentence_type == 'Q':
      info = parse_question(self.structure.tree, self.structure.shallow, sentence, False) 

      if info['error'] == '':
        self.insight.qtype = info['qtype']
        self.insight.aux_verb = info['aux_verb']
        self.insight.question = info['qword']

        self.insight.verb = info['verb']
        if self.insight.verb == '':
          self.insight.verb = info['vp']
        self.insight.vp = self.insight.verb

        self.insight.subject = info['subject']
        if self.insight.subject == '':
          self.insight.subject = info['np']
        self.insight.np = self.insight.subject

        self.insight.value = info['value']

        sa = self.original_sentence.split(" ")
        for s in sa:
          if s in concepts:
            self.insight.subject = concepts[s]
            self.insight.np = concepts[s]

      return True

    # otherwise parse what is assumed to be a command type sentence 
    save_struct = self.structure.shallow
    if self.structure.shallow not in command_rule_map:
      #print("Unrecognized command rule: [%s] for sentence %s" % (self.structure.shallow, self.original_sentence))

      # if not a recognized pattern maybe we can munge it
      # probably a question but could be of the form 'will you please do bla'
      if self.structure.shallow.startswith("NP "):
        # I suspect its of the form 'could you or will you do something'

        start_indx = self.structure.tree.find("(VP ")
        self.structure.tree = self.structure.tree[start_indx:]
        np = get_node("(NP ", self.structure.tree)

        # remove the NP from shallow rule
        self.structure.shallow = self.structure.shallow[3:]

        #print("Note! question converted to command. new rule:%s, new tree:%s " % (self.structure.shallow,self.structure.tree))

    if self.structure.shallow in command_rule_map:
      info = (command_rule_map[self.structure.shallow](self.structure.tree))
      # if not error
      if info['error'] == '':
        info['subject'] = remove_articles(info['subject'])

        self.structure.shallow = save_struct
        self.sentence_type = 'C'

        # TODO - verb concept maps must be intent specific 
        # this is too rough a granularity here!
        #self.insight.verb = command_concept_map.get(info['verb'].lower(), info['verb'].lower())
        self.insight.verb = info['verb'].lower()

        self.insight.squal = info['squal']
        self.insight.vp = info['verb']
        self.insight.subject = info['subject'].lower()
        self.insight.np = info['subject'] 
        self.insight.value = info['value']
        return True

    return self.handle_unknown_grammar(sentence)

if __name__ == "__main__":
    # unit tests kinda - validate subject verb
    print("Running NLU Unit Tests")
    print("======================")
    base_dir = os.getenv('PVX_BASE_DIR')
    si = SentenceInfo(base_dir)
    fpath = base_dir + '/framework/services/intent/nlp/shallow_parse/corpus_commands.txt'
    fh = open(fpath)
    failed = 0
    passed = 0
    total_lines = 0
    for line in fh.readlines():
        if line.strip() and not line.startswith("#"):
            la = line.split("|")
            if len(la) < 3:
                print("Ill formed input line! %s" % (line.strip(),))
            else:
                total_lines += 1
                si.parse_utterance(la[2].strip())
                expected_verb = la[0]
                expected_subject = la[1]
                if expected_subject != si.insight.subject or expected_verb != si.insight.verb:
                    failed += 1
                    print("[%s/%s]FAIL! Cmd:%s, Subject:%s <--- %s" % (failed, total_lines, si.insight.verb, si.insight.subject, line.strip()))
                else:
                    passed += 1

    ratio = 0.0
    if failed > 0 and total_lines > 0: 
        ratio = float(failed / total_lines)
    ratio = int( 100 * float( float(1.0) - ratio ) )
    print("Total:%s, Passed:%s, Failed:%s, %s%%" % (total_lines, passed, failed, ratio))
