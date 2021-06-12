'''
Created on Apr 4, 2021

@author: x2012x
'''
class ConductorException(Exception):
    pass

class UnsupportedAction(ConductorException):
    pass

class UnsupportedIntent(ConductorException):
    pass

class RegistrationExists(ConductorException):
    pass

class SpeakableException(ConductorException):
    def __init__(self, phrase):
        self.phrase = phrase    

class TTSFailure(SpeakableException):
    pass

class StateFailure(SpeakableException):
    pass

class CalendarFailure(SpeakableException):
    pass

class RoutineFailure(SpeakableException):
    pass
