'''
Created on Apr 14, 2021

@author: x2012x
'''
from errors.exceptions import StateFailure
from services.base import BaseService

class StateService(BaseService):
    ''' Provides access to state service operations.
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
    ''' 
    def __init__(self, conductor):
        super().__init__(conductor, 'state')

    def say_again(self):
        ''' Return the last collection of responses '''
        if not self.conductor.last_response:
            raise StateFailure('I haven\'t said anything.')
        return self.conductor.last_response