'''
Created on Apr 3, 2021

@author: x2012x
'''
from google.cloud import texttospeech
import hashlib
import os
from errors.exceptions import TTSFailure
from services.base import BaseService
from errors.reasons import get_general_failure
from services.audio import PlayRequest
from pathlib import Path

class TextToSpeechService(BaseService):
    ''' Provides access to TTS service operations.
    
    Service depends on Google's Text-To-Speech API. Your Google TTS JSON 
    config must be staged to 'resources/config/google-tts.json'
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
    ''' 
    def __init__(self, conductor):
        super().__init__(conductor, 'tts')
        # Google TTS client
        self._client = texttospeech.TextToSpeechClient.from_service_account_file('resources/config/google-tts.json')
        # Google TTS voice configuration
        self._voice = texttospeech.VoiceSelectionParams(language_code="en-GB", 
                                                        name="en-GB-Standard-F", 
                                                        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
        # Google Audio file configuration
        self._audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        # Google has a max character limit, service will fail any request that exceeds this limit, before sending to Google.
        self._character_limit = 5000
        # TODO: Need to setup a scheduler to periodically cleanup the cache.
        # TTS audio is cached in this directory for reuse. If the same phrase is being 
        # requested, the service will play from the cache instead of sending a request to Google.
        self._cache = 'resources/cache/tts_cache'
        Path(self._cache).mkdir(parents=True, exist_ok=True)

    def speak_response(self, response):
        ''' Speak the supplied response object.
        
        Arguments:
            response (Response): Response object to speak.
        '''
        self.speak(response.speech.text, response.background_audio, response.background_volume_shift)
        
    def speak(self, text_content, background_audio = None, background_volume_shift = 20):
        ''' Speak the supplied text_content while playing the optional background_audio track.
        
        text_content will be sent to the Google TTS service. Once the TTS audio file is 
        received from Google, an AudioService PlayRequest is constructed to process the returned audio
        file and the optional background track.
        
        Arguments:
            text_content (str): text to send to Google TTS.
            background_audio (str): path to audio file to play as background audio track
            background_volume_shift (int): amount of volume decrease that should be used for the 
                background track              
        '''        
        # Check for Google TTS max characters before transmitting request
        if len(text_content) > self._character_limit:
            # TODO: Get rid of prints and add a logger.
            print('Text to speak exceeds TTS character limit')
            raise TTSFailure(get_general_failure())
        try:
            # Get hash of the text_content being spoken.
            text_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
            # Use that hash to construct filenames for the text and audio file that will be stored in cache
            audio_file = os.path.join(self._cache, f'{text_hash}.mp3')
            text_file = os.path.join(self._cache, f'{text_hash}.txt')
            # If the current text doesn't exist in cache, send request to Google.
            if not os.path.exists(audio_file):
                synthesis_input = texttospeech.SynthesisInput(text=text_content)
                response = self._client.synthesize_speech(input=synthesis_input, voice=self._voice, audio_config=self._audio_config)
                with open(audio_file, "wb") as out:
                    out.write(response.audio_content)
                    # TODO: Get rid of prints and add a logger.
                    print(f'Created new recording at {audio_file}')
                with open(text_file, "w") as out:
                    out.write(text_content)
                    # TODO: Get rid of prints and add a logger.
                    print(f'Created transcription at {text_file}')
            else:
                # TODO: Get rid of prints and add a logger.
                print(f'Playing audio from cache {audio_file}')
            # Send a PlayRequest to the audio service to play the TTS audio and optional background track.
            self.conductor.audio.play(PlayRequest(audio_file, background_audio, background_volume_shift = background_volume_shift))
        except Exception:
            raise TTSFailure(text_content)
