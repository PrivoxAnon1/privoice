import requests, time, glob, os
from bus.Message import Message
from threading import Event
from bus.MsgBusClient import MsgBusClient
from interpreter import Interpret
from framework.util.utils import LOG, Config, get_wake_words, aplay, normalize_sentence, remove_pleasantries
from framework.services.intent.nlp.shallow_parse.nlu import SentenceInfo
from framework.services.intent.nlp.shallow_parse.shallow_utils import scrub_sentence, remove_articles
from framework.message_types import (
        MSG_UTTERANCE, 
        MSG_MEDIA, 
        MSG_RAW, 
        MSG_SYSTEM
        )

class UttProc:
    # English language specific intent parser. 
    def __init__(self, bus=None, timeout=5):
        self.skill_id = 'intent_service'

        # create bus client if none provided
        if bus is None:
            bus = MsgBusClient(self.skill_id)
        self.bus = bus

        self.intents = {}

        self.interpreter = Interpret()

        # set up logging into intent.log
        self.base_dir = os.getenv('PVX_BASE_DIR')
        self.tmp_file_path = self.base_dir + '/tmp/'
        log_filename = self.base_dir + '/tmp/logs/intent.log'
        self.log = LOG(log_filename).log

        # resources
        self.log.info("Intent Service Starting")
        self.earcon_filename = self.base_dir + "/framework/assets/earcon_start.wav"

        self.is_running = False

        # get configuration
        cfg = Config()
        self.crappy_aec = cfg.get_cfg_val('Advanced.CrappyAEC')
        remote_nlp = cfg.get_cfg_val('Advanced.NLP.UseRemote')
        self.use_remote_nlp = True
        if remote_nlp and remote_nlp == 'n':
            self.use_remote_nlp = False

        # we try to keep in sync with the system skill
        # so we can limit OOBs to verbs which have been
        # registered
        self.recognized_verbs = []

        # TODO need get_stop_aliases() method in framework.util.utils
        self.stop_aliases = ['stop', 'terminate', 'abort', 'cancel', 'kill', 'exit']

        # register message handlers
        self.bus.on('register_intent', self.handle_register_intent)
        self.bus.on('system', self.handle_system_message)
        self.bus.on('raw', self.handle_raw)


    def handle_system_message(self, message):
        # we try to stay in-sync with the system skill regarding OOBs
        data = message.data
        self.log.debug("Intent svc handle sys msg %s" % (data,))
        if data['skill_id'] == 'system_skill':
            # we only care about system messages - reserve and release oob
            self.log.debug("Intent service handle system message %s" % (message.data,))

            if data['subtype'] == 'reserve_oob':
                self.recognized_verbs.append( data['verb'] )

            if data['subtype'] == 'release_oob':
                del self.recognized_verbs[ data['verb'] ]


    def send_utt(self, utt):
        # sends an utterance to a 
        # target and handles edge cases
        target = utt.get('skill_id','*')
        if target == '':
            target = '*'
        if utt == 'stop':
            target = 'system_skill'
        self.bus.send(MSG_UTTERANCE, target, {'utt': utt,'subtype':'utt'})


    def send_media(self, info):
        self.bus.send(MSG_MEDIA, 'media_skill', info)


    def send_oob_to_system(self, utt, contents):
        info = {
                'error':'', 
                'subtype':'oob', 
                'skill_id':'system_skill', 
                'from_skill_id':self.skill_id, 
                'sentence_type':'I', 
                'sentence':contents, 
                'verb':utt, 
                'intent_match':''
                }
        self.bus.send(MSG_SYSTEM, 'system_skill', info)


    def get_question_intent_match(self, info):
        aplay(self.earcon_filename)  # should be configurable

        # see if a question matches an intent.
        skill_id = ''
        for intent in self.intents:
            stype, subject, verb = intent.split(":") 
            if stype == 'Q' and subject in info['subject'] and verb == info['qword']:
                # fuzzy match - TODO please improve upon this
                info['subject'] = subject
                skill_id = self.intents[intent]['skill_id']
                intent_state = self.intents[intent]['state']
                return skill_id, intent

        return skill_id, ''


    def get_intent_match(self, info):
        aplay(self.earcon_filename)  

        # for utterances of type command ('C')
        # an intent match is a subject:verb
        # and we don't fuzzy match
        skill_id = ''

        intent_type = 'C'
        if info['sentence_type'] == 'I':
            self.log.warning("Intent trying to match an informational statement which it is not designed to to! %s" % (info,))
            info['sentence_type'] == 'C'

        subject = remove_articles(info['subject'])
        if subject:
            subject = subject.replace(":",";")
            subject = subject.strip()

        key = intent_type + ':' + subject.lower() + ':' + info['verb'].lower().strip()

        if key in self.intents:
            self.log.info("Intent match. key is %s" % (key,))
            skill_id = self.intents[key]['skill_id']
            intent_state = self.intents[key]['state']
            self.log.info("Intent matched[%s] skill=%s, intent_state=%s" % (key,skill_id, intent_state))
            return skill_id, key

        self.log.info("No intent match. key is %s" % (key,))

        # no match 
        return skill_id, ''


    def handle_register_intent(self, msg):
        data = msg.data

        # the subject may contain colons which is 
        # what we prefer to use as a delimiter
        # so we convert them here
        subject = data['subject'].replace(":", ";")

        key = data['intent_type'] + ':' + subject.lower() + ':' + data['verb']

        self.log.error("INTENT. Trying to register key is %s" % (key,))

        if key in self.intents:
            self.log.warning("Intent clash! key=%s, skill_id=%s ignored!" % (key,data['skill_id']))
        else:
            self.intents[key] = {'skill_id':data['skill_id'], 'state':'enabled'}


    def run(self):
        self.log.info("Intent processor started - 'is_running' is %s" % (self.is_running,))
        while self.is_running:
            time.sleep(10.0)


    def handle_raw(self, msg):
        data = msg.data
        utt = data['utterance']
        contents = utt
        si = SentenceInfo(self.base_dir)
        res = self.interpreter.event_from_utt(utt)
        self.log.debug("Intent processor handle raw - result: %s" % (res,))

        if res == 'U_OOB' or res == 'Q_OOB':
            res = self.send_oob_to_system(utt, '[OOB]' + utt) 

        if res == 'Q_UTT':
            utt = self.interpreter.q_utt
            sentence_type = si.get_sentence_type(utt)

            self.log.debug("Sentence type = %s" % (sentence_type,))
            utt = normalize_sentence(utt)
            if sentence_type != 'Q':
                utt = remove_pleasantries(utt)

            # limited contraction support for now
            utt = utt.lower()
            utt = utt.replace("what's", "what is")
            utt = utt.replace("how's", "how is")
            utt = utt.replace("let's", "let us")
            utt = utt.replace("where's", "where is")

            si.parse_utterance(utt)

            info = {
                'error':'', 
                'sentence_type': si.sentence_type, 
                'sentence': si.original_sentence, 
                'normalized_sentence': si.normalized_sentence, 
                'qtype': si.insight.qtype.lower(), 
                'np': si.insight.np, 
                'vp': si.insight.vp, 
                'subject': si.insight.subject, 
                'squal': si.insight.squal, 
                'question': si.insight.question.lower(),
                'qword': si.insight.question.lower(), 
                'value': si.insight.value, 
                'raw_input': contents, 
                'verb': si.insight.verb.lower(),
                'aux_verb': si.insight.aux_verb,
                'rule': si.structure.shallow,
                'tree': si.structure.tree,
                'subtype':'', 
                'from_skill_id':'', 
                'skill_id':'', 
                'intent_match':''
                }

            print("INTENTSVC: %s" % (info,))
            # sentence types 
            # Q - question
            # C - command
            # I - info (currently unsupported)
            # U - unknown sentence structure
            # M - media request
            # O - oob (out of bounds) request
            if si.sentence_type == 'Q':
                self.log.debug("Question")
                info['skill_id'], info['intent_match'] = self.get_question_intent_match({'subject':info['subject'], 'qword':info['question']})
                res = self.send_utt(info) 

            elif si.sentence_type == 'C':
                self.log.debug("Command")
                info['skill_id'], info['intent_match'] = self.get_intent_match(info)
                res = self.send_utt(info) 

            elif si.sentence_type == 'M':
                self.log.debug("Media Command")
                info['skill_id'] = 'media_skill'
                info['from_skill_id'] = self.skill_id
                info['subtype'] = 'media_query'
                res = self.send_media(info) 

            elif si.sentence_type == 'O':
                self.log.debug("OOB Command")
                if utt in self.recognized_verbs:
                    self.send_oob_to_system(utt, contents)
                else:
                    self.log.warning("Ignoring not recognized OOB in intent_service '%s' not found in %s" % (utt,self.recognized_verbs))

            else:
                self.log.warning("Unknown sentence type or Informational sentence. Ignored for now.")

        self.bus.send(MSG_RAW, 'system_skill', {'utterance': utt})


if __name__ == '__main__':
    up = UttProc()
    up.is_running = True
    Event().wait()  # Wait forever

