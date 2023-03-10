import time, os
from threading import Thread, Lock
from framework.util.utils import LOG, Config, get_wake_words, aplay
"""
the interpreter takes in raw text messages
and converts them to the following message types ...

Q_OOB  - qualified out of band (example - computer stop)
U_OOB  - unqualified out of band (example - stop)
Q_UTT  - qualified utterance (computer what time is it)
WW     - wake word detected (just the wake word, not the 
         ww + utt, that is msg Q_UTT)

It should be noted this code is triggered by a RAW 
message and it does not repeat this message. this is 
basically a stateful stream parser designed to handle
the concept of a wake word and out of band (OOB) utterances.
"""
# these need to be registered but are hard coded for now
oobs = ['stop', 'start', 'cancel', 'terminate', 'abort', 
        'pause', 'resume', 'rewind', 'play', 'listen',
        'continue', 'halt',]

# watchdog timer
def wd_task(lock, shared_data):
    while True:
        with lock:
            shared_data['ctr'] -= 1
            if shared_data['ctr'] < 1:
                # Watchdog Timeout
                shared_data['ctr'] = 5
                shared_data['state'] = 'Idle'

        time.sleep(1)

class Interpret:
    def __init__(self,):
        self.cfg = Config()

        # set up logging into intent.log
        self.base_dir = os.getenv('PVX_BASE_DIR')
        self.tmp_file_path = self.base_dir + '/tmp/'
        log_filename = self.base_dir + '/tmp/logs/intent.log'
        self.log = LOG(log_filename).log

        self.watchdog_timeout = self.cfg.get_cfg_val('Advanced.Interpreter.WatchdogTimeout')
        self.allowed_noise_words = self.cfg.get_cfg_val('Advanced.Interpreter.WakeWordReach')

        self.shared_data = {'ctr':self.watchdog_timeout, 'state':'Idle'}

        # if you just say the wake word and nothing else we will beep
        # indicating we are now in utterance gathering mode.
        base_dir = os.getenv('PVX_BASE_DIR')
        self.ding_file = base_dir + "/framework/assets/ding.wav"

        # establish wake word(s)
        self.wake_words = []
        wws = get_wake_words()
        for ww in wws:
            self.wake_words.append( ww.lower() )

        self.log.error("Using wake word(s) %s" % (self.wake_words,))

        self.q_utt = ''
        self.wake_word_match = ''
        self.num_words_to_whack = 0
        self.last_utt = ''
        self.lock = Lock()
        self.watchdog_thread = Thread(target=wd_task, args=(self.lock, self.shared_data)).start()

    def clean_utt(self, utt):
        utt = utt.lower().strip()
        utt = utt.replace(",", " ")
        utt = utt.replace(".", " ")
        utt = utt.replace(":", " ")
        utt = utt.replace(";", " ")
        utt = utt.replace("!", " ")
        utt = utt.replace("?", " ")
        utt = utt.replace("  ", " ")
        if utt.startswith(" "):
            utt = utt[1:]
        return utt.strip()

    def is_wake_word(self, utt):
        utt = self.clean_utt(utt)
        words = utt.split(" ")
        self.num_words_to_whack = min( [self.allowed_noise_words, len(words)] )
        words = words[0:self.num_words_to_whack]
        # find wake_word(s) in utterance
        for wake_word in self.wake_words:
            try:
                self.num_words_to_whack = words.index(wake_word) + 1
                self.wake_word_match = wake_word
                return True
            except:
                pass

        return False

    def is_oob(self, utt):
        # return '' if not, else the oob
        utt = self.clean_utt(utt)
        try:
            indx = oobs.index(utt.split(" ")[0].lower())
            return oobs[indx]
        except:
            return ''

    def event_from_utt(self, utt):
        self.shared_data['ctr'] = self.watchdog_timeout
        self.last_utt = utt
        if self.shared_data['state'] == 'Idle':
            if self.is_wake_word(utt):
                # got the wake word in there somewhere
                words = utt.split(" ")[self.num_words_to_whack:]
                sentence = " ".join(words)
                if len(sentence) == 0:
                    # if utterance is wake word match only
                    self.shared_data['state'] = 'WakeWordActive'
                    #return 'MSG[WW]%s' % (self.wake_word_match,)
                    aplay(self.ding_file)
                    return 'WW'
                else:
                    # wake word detected but could still be oob
                    oob = self.is_oob(utt)
                    if oob != '':
                        #return 'MSG[Q_OOB]%s' % (oob,)
                        return 'Q_OOB'
                    else:
                        # wake word detected not oob
                        #return 'MSG[Q_UTT]%s' % (sentence,)
                        self.q_utt = sentence
                        return 'Q_UTT'
            else:
                # wake word not detected, is it oob?
                oob = self.is_oob(utt)
                if oob != '':
                    #return 'MSG[U_OOB]%s' % (oob,)
                    return 'U_OOB'
        else:
            # already got the wake word last utterance
            self.shared_data['state'] = 'Idle'
            oob = self.is_oob(utt)
            if oob != '':
                #return 'MSG[Q_OOB]%s' % (oob,)
                return 'Q_OOB'

            # otherwise, we have a qualified utt
            #return 'MSG[Q_UTT]%s' % (utt,)
            self.q_utt = utt
            return 'Q_UTT'

