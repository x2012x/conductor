'''
Created on May 30, 2021

@author: x2012x
'''
import random
from errors.exceptions import RoutineFailure
from services.base import BaseService, Response
from errors.reasons import get_general_failure

# TODO: Refactor this such that phrases are stored outside of code (e.g. in a DB) and build a service for accessing them.

# Collection of good morning phrases.
GOOD_MORNING = ['I hope you slept well.',
                'I hope you\'re rested.']

# Collection of day descriptions.
DAY_TYPES = ['a great',
             'an awesome',
             'a fantastic']

# Collection of good night phrases.
GOOD_NIGHT = ['Sleep well.',
              'Good night.',
              'Sleep tight.']

# Collection of sleeping tips.
NIGHT_TIPS = ['',
              'If you have trouble sleeping, try counting sheep.']


class Routine(object):
    ''' Defines the attributes of a routine.
    
    Arguments:
        name (str): name of the routine
        target (object): target to invoke for this routine
    '''
    def __init__(self, name, target):
        self.name = name
        self.target = target


class RoutinesService(BaseService):
    ''' Provides access to routine service operations.
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
    ''' 
    def __init__(self, conductor):
        super().__init__(conductor, 'routines')
        # Map of registered routines
        self._routines = {}
        self.__register_routine(Routine('good morning', self._good_morning))
        self.__register_routine(Routine('good night', self._good_night))
        
    def __register_routine(self, routine):
        ''' Register the supplied routine with the service.
        
        Arguments:
            routine (Routine): routine to register.
        '''
        self._routines[routine.name] = routine
        
    def _good_morning(self):
        ''' Target for good morning routine.
        
        Builds a collection of responses which wishes the user good morning and tells the current time.
        '''
        return [Response('Good morning.'), Response(random.choice(GOOD_MORNING)), self.conductor.calendar.current(), Response('Have '+random.choice(DAY_TYPES)+' day.')]
    
    def _good_night(self):
        ''' Target for good night routine.
        
        Wishes the user good night.
        '''
        return [Response(random.choice(GOOD_NIGHT) + ' ' + random.choice(NIGHT_TIPS))]
        
    def invoke(self, name):
        ''' Invoke a routine, identified by name.
        
        Arguments:
            name (str): name of the routine to invoke
            
        Returns:
            return result from the invoked routine.
        '''
        response = None
        try:
            response = self._routines[name].target()
        except Exception:
            raise RoutineFailure(get_general_failure())
        return response    
