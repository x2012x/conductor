'''
Created on May 22, 2021

@author: x2012x
'''
from services.base import BaseService, Response
from errors.exceptions import CalendarFailure
from errors.reasons import get_general_failure
from datetime import datetime


class CalendarService(BaseService):
    ''' Provides access to calendar service operations.
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
    ''' 
    def __init__(self, conductor):
        super().__init__(conductor)
        self._time_format = '%I %M %p'
        self._day_format = '%A %B %d'
        
    def current(self):
        ''' Get the current date and time '''
        try:
            return Response(datetime.now().strftime(f'It\'s {self._time_format} on {self._day_format}'))
        except Exception:
            raise CalendarFailure(get_general_failure())
    
    def current_time(self):
        ''' Get the current time '''
        try:
            return Response(datetime.now().strftime(f'It\'s {self._time_format}'))
        except Exception:
            raise CalendarFailure(get_general_failure())
    
    def current_day(self):
        ''' Get the current date '''
        try:
            return Response(datetime.now().strftime(f'It\'s {self._day_format}'))
        except Exception:
            raise CalendarFailure(get_general_failure())
    