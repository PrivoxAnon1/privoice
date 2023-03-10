import threading, time, os, re
from threading import Event, Thread
import se_tts_constants
from datetime import datetime
from queue import Queue
from framework.util.utils import Config, chunk_text
from bus.MsgBusClient import MsgBusClient
from framework.message_types import MSG_MEDIA, MSG_SKILL
from se_tts_session_table import TTSSessionTable
from se_tts_session_methods import TTSSessionMethods

class TTSSession(TTSSessionTable, TTSSessionMethods, threading.Thread):
    def __init__(self, owner, tts_sid, msid, session_data, internal_event_callback, log):
        self.log = log
        super(TTSSession, self).__init__()
        threading.Thread.__init__(self)
        self.skill_id = "tts_session"
        self.bus = MsgBusClient(self.skill_id)
        self.state = 'idle'

        self.engine = None
        self.model = None
        self.voice = None

        self.exit_flag = False
        self.paused = False
        self.pause_ack = False
        self.owner = owner
        self.tts_sid = tts_sid
        self.msid = msid
        self.session_data = session_data
        self.index = 0
        self.internal_event_callback = internal_event_callback
        self.paused_requestor = None
        self.lock = threading.RLock()

        # we run remote and local tts in parallel. this will hold maybe
        # both responses, maybe one or maybe none. None would be a time out
        self.tts_wait_q_local = Queue()
        self.tts_wait_q_remote = Queue()

        self.state = se_tts_constants.STATE_IDLE
        self.valid_states = se_tts_constants.valid_states
        self.valid_events = se_tts_constants.valid_events

        cfg = Config()
        # we always fall back if remote fails but local only means 
        # don't even try remote which will be faster than a local
        # fall back which is effectively a remote time out.
        self.remote_tts = None
        self.use_remote_tts = False

        from framework.services.tts.local.default import local_speak_dialog
        self.local_speak = local_speak_dialog

        self.tmp_file_path = os.getenv('PVX_BASE_DIR') + '/tmp'
        self.local_filename = ''

        self.bus.on(MSG_SKILL, self.handle_skill_msg)

    def wait_paused(self, requestor):
        # set up to handle pause responses from
        # both local and remote processes
        self.internal_pause = False
        self.external_pause = False
        self.paused = True
        self.paused_requestor = requestor
        # tell media player too
        self.send_session_pause()
        # this will cause an internal event to fire once
        self.pause_ack = True

    def play_file(self,filename):
        self.log.debug("TTSSession play_file() state=%s, self.msid=%s, curr_sess.msid=%s, filename=%s" % (self.state, self.msid, self.msid, filename))
        if self.state == se_tts_constants.STATE_ACTIVE:
            if self.msid == 0:
                self.log.info("TTSSession Warning, invalid session ID (0). Must reestablish media session!")
                self.paused_filename = filename
                self.__change_state(se_tts_constants.STATE_WAIT_MEDIA_START)
                self.send_media_session_request()
            else:
                info = {
                    'file_uri':filename,
                    'media_type':'wav',
                    'subtype':'media_player_command',
                    'command':'play_media',
                    'correlator':self.correlator,
                    'session_id':self.msid,
                    'skill_id':'media_player_service',
                    'from_skill_id':self.skill_id,
                    'delete_on_complete':'true'
                    }
                self.bus.send(MSG_MEDIA, 'media_player_service', info)
                self.log.debug("TTSSession play_file() exit - play state=%s, filename = %s" % (self.state, filename))
        else:
            self.log.warning("Play file refusing to play because state is not active ---> %s" % (self.state,))

    def get_remote_tts(self, chunk, model=None, voice=None):
        self.local_filename = datetime.now().strftime("save_tts/local_outfile_%Y-%m-%d_%H-%M-%S_%f.wav")
        self.local_filename = "%s/%s" % (self.tmp_file_path, self.local_filename)
        self.model = model
        self.voice = voice

        th2 = None
        th2 = Thread(target=self.local_speak, args=(chunk, self.local_filename, self.tts_wait_q_local, self.model, self.voice))
        th2.daemon = True
        th2.start()
        result = ''

        try:
            result = self.tts_wait_q_local.get(block=True, timeout=se_tts_constants.REMOTE_TIMEOUT)
        except:
            self.log.warning("Creepy Internal Error 101 - TTSSession local timed out too!")
            return False

        self.log.debug("TTSSession create wave file, Final result: {}, text:{}, filename:{}".format(result,chunk,self.local_filename))
        return self.local_filename

    def send_media_session_request(self):
        info = {
            'error':'',
            'subtype':'media_player_command',
            'command':'start_session',
            'correlator':self.correlator,
            'skill_id':'media_player_service',
            'from_skill_id':self.skill_id
            }
        self.bus.send(MSG_MEDIA, 'media_player_service', info)

    def stop_media_session(self):
        self.paused = True
        self.log.debug("TTSSession told to stop media session!, state=%s, mpsid:%s" % (self.state, self.msid))

        if self.msid != 0:
            info = {
                    'error':'',
                    'subtype':'media_player_command',
                    'command':'stop_session',
                    'correlator':self.correlator,
                    'session_id':self.msid,
                    'skill_id':'media_player_service',
                    'from_skill_id':self.skill_id,
                    }
            self.bus.send(MSG_MEDIA, 'media_player_service', info)
            self.msid = 0
        else:
            # else no active media session to stop
            self.log.warning("TTSSession no media player session to stop (id=%s)" % (self.msid,))

        self.session_data = []
        self.index = 0

    def send_session_pause(self):
        info = {
                'error':'',
                'subtype':'media_player_command',
                'command':'pause_session',
                'correlator':self.correlator,
                'session_id':self.msid,
                'skill_id':'media_player_service',
                'from_skill_id':self.skill_id,
                }
        self.bus.send(MSG_MEDIA, 'media_player_service', info)

    def send_session_resume(self):
        info = {
                'error':'',
                'subtype':'media_player_command',
                'command':'resume_session',
                'correlator':self.correlator,
                'session_id':self.msid,
                'skill_id':'media_player_service',
                'from_skill_id':self.skill_id,
                }
        self.bus.send(MSG_MEDIA, 'media_player_service', info)

    def add(self, i):
        with self.lock:
            self.session_data.extend(i)

    def remove(self, i):
        with self.lock:
            self.session_data.remove(i)

    def reset(self, owner):
        with self.lock:
            self.owner = owner
            self.session_data = []
            self.index = 0
            self.msid = 0
            self.tts_sid = 0
            self.correlator = 0
            self.paused = True
            self.state = se_tts_constants.STATE_IDLE

    def run(self):
        while not self.exit_flag:
            #print("TIC paused=%s, index=%s, data=%s" % (self.paused,self.index, self.session_data))
            if self.pause_ack:
                self.pause_ack = False
                self.handle_event(se_tts_constants.EVENT_INTERNAL_PAUSE, {'tsid':self.tts_sid, 'msid':self.msid})
            if not self.paused:
                if len(self.session_data) == self.index and self.index != 0:
                    # End of q reached!
                    self.index = 0
                    self.session_data = []
                    self.handle_event(se_tts_constants.INTERNAL_EVENT_ENDED, {'tsid':self.tts_sid, 'msid':self.msid})
                else:
                    if len(self.session_data) > 0:
                        sentence = self.session_data[self.index]
                        tmp_file = self.get_remote_tts(sentence, model=self.model, voice=self.voice)
                        if not self.paused:
                            self.play_file( tmp_file )
                            self.index += 1
            time.sleep(0.01)

    def handle_skill_msg(self,msg):
        data = msg.data
        msg_correlator = data.get("correlator","")

        if data['skill_id'] == self.skill_id:

            if data['subtype'] == 'media_player_command_response':
                # these come to us from the media service

                if self.correlator != self.tts_sid:
                    self.log.debug("TTSSession Internal issue. self.cor [%s] <> self.curr_sess.tts_sid [%s]" % (self.correlator, self.tts_sid))

                if self.correlator != msg_correlator:
                    self.log.error("TTSSession correlators dont match! Ignoring message. self.cor[%s] <> msg.cor[%s]" % (self.correlator, msg_correlator))
                    return False

                if msg.data['response'] == 'session_confirm':
                    self.handle_event(se_tts_constants.EVENT_MEDIA_CONFIRMED, data)

                elif msg.data['response'] == 'session_reject':
                    self.handle_event(se_tts_constants.EVENT_MEDIA_DECLINED, data)

                elif msg.data['response'] == 'session_paused':
                    self.handle_event(se_tts_constants.EVENT_MEDIA_PAUSED, data)

                elif msg.data['response'] == 'session_ended':
                    if msg.data['reason'] == 'eof':
                        self.handle_event(se_tts_constants.EVENT_MEDIA_ENDED, data)
                    else:
                        self.handle_event(se_tts_constants.EVENT_MEDIA_CANCELLED, data)

                elif msg.data['response'] == 'stop_session':
                    self.log.warning("TTSSession Creepy Internal Error 102 - the media player reported stop_session for no reason.")

                else:
                    self.log.warning("TTSSession Creepy Internal Error 103 - unknown media response = %s" % (msg.data['response'],))

