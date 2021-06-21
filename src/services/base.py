'''
Created on Apr 17, 2021

@author: x2012x
'''
import json

class BaseService(object):
    ''' Base class that all Services should be derived from.
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
        name (str): name of the service, also used as the service attribute name on the Conductor.
    ''' 
    def __init__(self, conductor, name):
        self.conductor = conductor
        self.name = name


class ResponseText(object):
    ''' Stores service response text, which is an attribute of the overall service response '''
    def __init__(self, text = ''):
        self.text = text


class Response(object):
    ''' Service response containing any text that should be spoken and the details of an optional
    background audio track.
    
    Arguments:
        spoken_text (str): text that should be spoken by the TTS.
        background_audio (str): path to an audio file that should be played in the background
            while the spoken_text is being played. Background tracks are played in a loop 
            until the primary track finishes.
        background_volume_shift (int): amount of volume decrease that should be used for the 
            background track
    '''
    def __init__(self, spoken_text = '', background_audio = None, background_volume_shift = 20):
        self.speech = ResponseText(spoken_text)
        self.background_audio = background_audio
        self.background_volume_shift = background_volume_shift
        
    def toJSON(self):
        ''' Returns a JSON representation '''
        return json.dumps(self, default=lambda o: o.__dict__)
