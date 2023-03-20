

General flow is 

                                     |---> media 
Recognizer ---> Intent ---> Skill ---|
                                     |---> tts

intent: the intent service. converts raw messages to intent messages or oobs
leans on the nlp/nlu shallow parse method. see nlp/ for more info.

media: the media service. plays wav, mp3 and video streams.

recognizer: speech recognizer. converts wav data to text messages

skill_manager: handles installing and running/stopping skills

tts: the tts service. be afraid, be very afraid.


