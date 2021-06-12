'''
Created on Apr 14, 2021

@author: x2012x
'''
import random
from errors.exceptions import TTSFailure

# TODO: Refactor this such that reasons are stored outside of code (e.g. in a DB) and build a service for accessing them.

GENERAL_FAILURES = ['I can\'t do that right now, try again later.',
                    'I don\'t feel like handling that request.',
                    'It\'s not a good time right now.']

EXCEPTION_REASONS = {
    TTSFailure: ['I\'m not feeling well.',
                 'My allergies are acting up.']
}

def get_general_failure():
    ''' Get a random reason for a general failure. '''
    return random.choice(GENERAL_FAILURES)

def get_reason(exception):
    ''' Get a random reason for the supplied exception type. '''
    return random.choice(EXCEPTION_REASONS[type(exception)])
