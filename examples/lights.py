'''
Created on Dec 30, 2020

@author: x2012x
'''
import requests
from handlers.base import BaseHandler
from services.base import BaseService, Response
from errors.reasons import get_general_failure
from errors.exceptions import SpeakableException

# Intents
CHANGE_LIGHT_STATE = 'ChangeLightState'

LIFX = 'lifx'
HOUSE = 'house'
LIGHTS = {LIFX: {HOUSE: 'location_id:XXXXXXXXXXXXXXXXXXXXXXXXX'}} # TODO: Your LIFX house location_id is needed here.


class LightFailure(SpeakableException):
    pass


class LightsHandler(BaseHandler):
    
    def __init__(self, conductor):
        super().__init__(conductor, 'lights', {CHANGE_LIGHT_STATE})

    def power(self, lights, duration, power):
        return self.conductor.lights.power(lights, duration, power)
        
    def _handle_intent(self, intent):
        if intent['intent']['name'] == CHANGE_LIGHT_STATE:
            return self.power('house', 2.0, intent['slots']['power'])


class LightsService(BaseService):

    def __init__(self, conductor):
        super().__init__(conductor, 'lights')
        self.config = {LIFX: {'token': '<LIFX_API_TOKEN>'}} # TODO: Your LIFX API token is needed here.
        self._base_url = 'https://api.lifx.com/v1/lights/'
        self._timeout = 3.00
        
    def _lifx_headers(self):
        return {'Authorization': f'Bearer {self.config[LIFX]["token"]}'}        
        
    def power(self, lights, duration, power):
        try:
            lifx_url = f'{self._base_url}{LIGHTS[LIFX][lights]}/state'
            requests.put(lifx_url, 
                         params = {'duration': duration,
                                   'power': power},
                         headers=self._lifx_headers(),
                         timeout = self._timeout)
        except Exception:
            raise LightFailure(get_general_failure())
        return Response()
            
