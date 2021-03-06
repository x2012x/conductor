'''
Created on Jun 4, 2021

@author: x2012x
'''
import logging
from handlers.base import BaseHandler
from services.base import Response

logger = logging.getLogger(__name__)

class TextToSpeechHandler(BaseHandler):
    ''' Handler for processing TTS requests '''
    
    def __init__(self, conductor):
        super().__init__(conductor, 'tts')
        
    def speak(self, text_content):
        ''' Handle a request to speak the supplied text_content
        
        Arguments:
            text_content (str): string to pass to the TTS service for processing.
        '''
        try:
            self.conductor.tts.speak(text_content)
        except Exception as e:
            logger.error(f'Failed to speak request: {e}')
        return Response()
    
    def _handle_intent(self, intent):
        return Response()
