'''
Created on Dec 31, 2020

@author: x2012x
'''
import logging
import pychromecast
import threading
import time
from handlers.base import BaseHandler
from services.base import BaseService, Response
from errors.exceptions import SpeakableException
from errors.reasons import get_general_failure

logger = logging.getLogger(__name__)

# Intents
STOP_VIDEO = 'StopVideo'
VIDEO_ACTION = 'VideoAction'

LIVING_ROOM = 'living_room'
DEVICES = {LIVING_ROOM: '0.0.0.0'} # TODO: Your living room Chromecast's IP.


class ChromecastFailure(SpeakableException):
    pass


class ChromecastHandler(BaseHandler):

    def __init__(self, conductor):
        super().__init__(conductor, 'chromecast', {STOP_VIDEO, VIDEO_ACTION})
        
    def stop(self, device, muted, force=False):
        return self.conductor.chromecast.stop(device, muted, force)
    
    def action(self, device, action):
        return self.conductor.chromecast.action(device, action)
        
    def _handle_intent(self, intent):
        if intent['intent']['name'] == STOP_VIDEO:
            return self.stop(LIVING_ROOM, False, True)
        elif intent['intent']['name'] == VIDEO_ACTION:
            return self.action(LIVING_ROOM, intent['slots']['action'])
        

def connect(device):
    cc = pychromecast.Chromecast(device.address)
    cc.wait()
    cc.media_controller.block_until_active(1)
    return cc    


def stop_on_device(device, muted, force):
    cc = connect(device)
    if cc.media_controller.status.content_id == device.previous_media or force:
        cc.quit_app()
        cc.set_volume_muted(muted)
        time.sleep(3)
        device.previous_media = None
    else:
        logger.error('Skipping stop: Content ID unknown')
    cc.disconnect()
        
        
def action_on_device(device, action):
    cc = connect(device)
    if action == 'play':
        if cc.media_controller.status.player_is_paused:
            cc.media_controller.play()
        else:
            logger.warn('Skipping play: Not currently paused.')
    elif action == 'pause':
        if cc.media_controller.status.player_is_playing:
            cc.media_controller.pause()
        else:
            logger.warn('Skipping pause: Not currently playing.')
    else:
        logger.error(f'Skipping {action}: Action unknown.')
    cc.disconnect()
        

class Device():
    
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.previous_media = None
        
        
class ChromecastService(BaseService):

    def __init__(self, conductor):
        super().__init__(conductor, 'chromecast')
        self.devices = {k: Device(k, v) for (k, v) in DEVICES.items()}
        
    def stop(self, device, muted, force=False):
        try:
            threading.Thread(target=stop_on_device, args=(self.devices[device], muted, force)).start()
        except Exception:
            raise ChromecastFailure(get_general_failure())
        return Response()
    
    def action(self, device, action):
        try:
            threading.Thread(target=action_on_device, args=(self.devices[device], action)).start()
        except Exception:
            raise ChromecastFailure(get_general_failure())
        return Response()        

