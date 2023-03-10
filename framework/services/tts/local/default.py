#!/usr/bin/env python3
import datetime, socket, time, TTS, sys
from pathlib import Path
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer


def produce_wav(text, io_buff, speaker_index, language, model_name):
    # convert text to a wav file using whisper
    path = Path(TTS.__file__).parent  / ".models.json"
    manager = ModelManager(path)
    speakers_file_path = None
    vocoder_path = None
    vocoder_config_path = None
    encoder_path = None
    encoder_config_path = None
    use_cuda = False
    #use_cuda = True

    model_path, config_path, model_item = manager.download_model(model_name)
    vocoder_name = model_item["default_vocoder"]

    synthesizer = Synthesizer(
            model_path,
            config_path,
            speakers_file_path,
            vocoder_path,
            vocoder_config_path,
            encoder_path,
            encoder_config_path,
            use_cuda,
        )
    wav = synthesizer.tts(text, speaker_index)
    synthesizer.save_wav(wav, io_buff)


def local_speak_dialog(text, filename, wait_q, model=None, voice=None):
    language = "en"
    try:
        produce_wav(text, filename, voice, language, model)
    except:
        #log_msg("Transcription Exception Caught!")
        pass

    wait_q.put({'service':'local', 'status':'success'})

