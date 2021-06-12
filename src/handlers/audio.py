'''
Created on Jun 2, 2021

@author: x2012x
'''
from handlers.base import BaseHandler

# Intents
AUDIO_STOP = 'AudioStop'


class AudioHandler(BaseHandler):
    ''' Handler for processing audio requests '''
    
    def __init__(self, conductor):
        super().__init__(conductor, 'audio', {AUDIO_STOP})
        
    def stop(self):
        ''' Request that current audio playback be stopped '''
        return self.conductor.audio.shutdown()
    
    def _handle_intent(self, intent):
        if intent['intent']['name'] == AUDIO_STOP:
            return self.stop()