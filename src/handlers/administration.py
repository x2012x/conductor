'''
Created on Jan 1, 2021

@author: x2012x
'''
from handlers.base import BaseHandler
import threading
from services.base import Response


class AdministrationHandler(BaseHandler):
    ''' Handler for processing system administration requests '''
        
    def __init__(self, conductor):
        super().__init__(conductor, 'admin')

    def shutdown(self):
        ''' Shutdown the conductor '''
        threading.Thread(target=self.conductor.shutdown).start()
        
    def _handle_intent(self, intent):
        return Response()
