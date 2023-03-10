import threading, webrtcvad, whisper, signal, numpy, queue, time, glob, sys, os
from datetime import datetime
from threading import Thread
from io import BytesIO
from bus.Message import Message
from bus.MsgBusClient import MsgBusClient
from framework.message_types import MSG_RAW
from framework.util.utils import Config
""" recognizer.py - self contained local speech to text recognizer.
run like this ...
  arecord -f s16_le -c 1 -r 16000 | python recognizer.py
"""
class StopThread(Exception):
    def __init__(self):
        return

    def __str__(self):
        return "False"

def read_stdin_stream(handler, chunk_size=320):
    with sys.stdin as f:
        while True:
            buffer = f.buffer.read(chunk_size)
            if buffer == b'':
                break
            handler(buffer)

class KillableThread(threading.Thread):
    def _bootstrap(self, stop_thread=False):
        def stop():
            nonlocal stop_thread
            stop_thread = True
        self.stop = stop

        def tracer(*_):
            if stop_thread:
                raise StopThread()
            return tracer
        sys.settrace(tracer)
        super()._bootstrap()

class SilenceDetector:
    def __init__(self):
        self.cfg = Config()
        #self.vad_mode = VAD_MODE           # 1=loose, 3=tight
        self.vad_mode = self.cfg.get_cfg_val('Advanced.Recognizer.VadMode')
        self.min_utterance_bytes = self.cfg.get_cfg_val('Advanced.Recognizer.MinUtteranceBytes')
        self.model_name = self.cfg.get_cfg_val('Advanced.Recognizer.ModelName')
        self.lang = self.cfg.get_cfg_val('Advanced.Recognizer.Language')
        self.reset_ctr = self.cfg.get_cfg_val('Advanced.Recognizer.ResetTimeoutCounter')
        self.reset_to = self.cfg.get_cfg_val('Advanced.Recognizer.ResetSleepTime')

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(self.vad_mode)   

        self.state = 'idle'                # collecting or idle
        self.xcribe_text = ''              # stt result

        self.speech_buff = b''
        self.sample_rate = 16000           # required
        self.audio_normalised = ''
        self.queue = queue.Queue()

        #print("Recognizer using model %s" % (self.model_name,))
        self.model = whisper.load_model(self.model_name)

        self.consumer = Thread(target=self.convert_stt)
        self.consumer.start()

        self.skill_id = 'SilenceDetector'
        self.bus = MsgBusClient(self.skill_id)
        time.sleep(1)  # its a bus not a ferari
        print("BUS:%s, MIN_WAV:%s bytes, VAD:%s, MODEL:%s, RST:%s seconds" % (self.bus.status, self.min_utterance_bytes, self.vad_mode, self.model_name, (self.reset_ctr * self.reset_to)))

    def reset_vad(self):
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(self.vad_mode)  

    def xcribe(self):
        try:
            self.xcribe_text = self.model.transcribe(
                                     self.audio_normalised, 
                                     fp16=False, 
                                     task="transcribe",
                                     language=self.lang)["text"].strip()
        except:
            print("Caught transcribe exception")
            pass

    def convert_stt(self):
        print('STT Transcriber is Running')
        while True:
            wav_data = self.queue.get()

            # check for stop
            if wav_data is None:
                break
            wd_size = len(wav_data)

            # Convert buffer to float32 using NumPy 
            audio_as_np_int16 = numpy.frombuffer(wav_data, dtype=numpy.int16)
            audio_as_np_float32 = audio_as_np_int16.astype(numpy.float32)

            # Normalize float32s so values are between -1.0 and +1.0 
            max_int16 = 2**15
            self.audio_normalised = audio_as_np_float32 / max_int16

            #print("Start transcribing ...")
            start = time.time()
            self.xcribe_text = ''
            test3 = KillableThread(target=self.xcribe)
            test3.start()

            to_ctr = 0
            while to_ctr < self.reset_ctr and self.xcribe_text == '':
                time.sleep(self.reset_to)
                to_ctr += 1

            test3.stop()
            test3.join()
            
            print("[%s][%02f secs]Took %02f secs: %s" % (wd_size, wd_size / 32000, time.time() - start, self.xcribe_text))

            self.xcribe_text = self.xcribe_text.strip()
            if self.xcribe_text and len(self.xcribe_text) > 0:
                if self.xcribe_text[0] != '.':
                    if self.bus.status == 'Connected':
                        self.bus.send(MSG_RAW, 'intent_service', {'utterance': self.xcribe_text})
                else:
                    self.speech_buff = b''
                    self.reset_vad()
                    self.state = 'idle'
                    #print("Reset1")
            else:
                self.speech_buff = b''
                self.reset_vad()
                self.state = 'idle'
                #print("Reset2")

        #print('STT Transcriber: Shutting Down!')

    def process_data(self, buffer):
        if self.state == 'idle':
            if self.vad.is_speech(buffer, self.sample_rate):
                self.state = 'collecting'
                self.speech_buff = buffer
        else:
            if not self.vad.is_speech(buffer, self.sample_rate):
                if len(self.speech_buff) > self.min_utterance_bytes:
                    b1 = self.speech_buff[ : ]
                    self.queue.put(b1)
                    self.state = 'idle'
                else:
                    self.speech_buff = b''
            else:
                self.speech_buff += buffer

if __name__ == "__main__":
    sd = SilenceDetector()
    read_stdin_stream(sd.process_data)
    print("Exiting!")

