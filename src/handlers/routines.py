'''
Created on May 30, 2021

@author: x2012x
'''
from handlers.base import BaseHandler

# Intents
ROUTINE_INVOKE = 'RoutineInvoke'


class RoutinesHandler(BaseHandler):
    ''' Handler for processing routine requests '''
    
    def __init__(self, conductor):
        super().__init__(conductor, 'routines', {ROUTINE_INVOKE})
        
    def invoke(self, name):
        ''' Execute a routine by name 
        
        Arguments:
            name (str): name of the routine to execute
        '''
        return self.conductor.routines.invoke(name)

    def _handle_intent(self, intent):
        if intent['intent']['name'] == ROUTINE_INVOKE:
            return self.invoke(intent['slots']['name'])