'''
Created on Apr 14, 2021

@author: x2012x
'''
from handlers.base import BaseHandler

# Intents
SAY_AGAIN = 'SayAgain'


class StateHandler(BaseHandler):
    ''' Handler for processing state requests '''
    
    def __init__(self, conductor):
        super().__init__(conductor, 'state', {SAY_AGAIN})

    def say_again(self):
        ''' Return the last collection of responses '''
        return self.conductor.state.say_again()
        
    def _handle_intent(self, intent):
        if intent['intent']['name'] == SAY_AGAIN:
            return self.say_again()
