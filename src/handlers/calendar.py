'''
Created on May 22, 2021

@author: x2012x
'''
from handlers.base import BaseHandler

# Intents
CALENDAR_CURRENT = 'CalendarCurrent'
CALENDAR_CURRENT_TIME = 'CalendarCurrentTime'
CALENDAR_CURRENT_DAY = 'CalendarCurrentDay'


class CalendarHandler(BaseHandler):
    ''' Handler for processing calendar requests '''
    
    def __init__(self, conductor):
        super().__init__(conductor, 'calendar', {CALENDAR_CURRENT, CALENDAR_CURRENT_TIME, CALENDAR_CURRENT_DAY})
        
    def current(self):
        ''' Get the current date and time '''
        return self.conductor.calendar.current()
    
    def current_time(self):
        ''' Get the current time '''
        return self.conductor.calendar.current_time()
    
    def current_day(self):
        ''' Get the current date '''
        return self.conductor.calendar.current_day()    
        
    def _handle_intent(self, intent):
        if intent['intent']['name'] == CALENDAR_CURRENT:
            return self.current()        
        elif intent['intent']['name'] == CALENDAR_CURRENT_TIME:
            return self.current_time()
        elif intent['intent']['name'] == CALENDAR_CURRENT_DAY:
            return self.current_day()
        