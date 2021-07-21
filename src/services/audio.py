'''
Created on Apr 3, 2021

@author: x2012x
'''
import logging
import time
import threading
from collections import deque
from services.base import BaseService
from audioplayer import AudioPlayer

logger = logging.getLogger(__name__)

class PlayRequest(object):
    ''' Defines parameters for an audio playback request
    
    Arguments:
        primary (str): path to the audio file to use as the primary track
        background (str): path the audio file to use as the background track. Background 
            tracks are played in a loop until the primary track finishes.
        delay (int): amount of time, in seconds, to wait after starting the background 
            track before starting the primary track.
        background_volume_shift (int): amount of volume decrease that should be used for the 
            background track        
    '''
    def __init__(self, primary, background = None, delay = 2.5, background_volume_shift = 20):
        self.primary = primary
        self.background = background
        self.delay = delay
        self.background_volume_shift = background_volume_shift
        
        
class Player(threading.Thread):
    ''' Player thread which processes PlayRequests contained on the AudioService's queue 
    
    Arguments:
        service (AudioService): reference to the audio service containing a _queue 
            of PlayRequests to process
    '''
    def __init__(self, service):
        super().__init__()
        self._service = service
        self._process_queue = True        
        self._primary = None
        self._background = None
        self._volume = 25
        
    def stop(self):
        ''' NOTE: Until state can be obtained from audioplayer, or a different lib 
            is used, stopping the Player will only stop processing the queue. The 
            current request track will still be finished.'''
        logger.debug('Stop processing player queue')
        self._process_queue = False
        
    def run(self):
        while self._process_queue:
            try:
                request = self._service._queue.popleft()
                self._play(request.primary, request.background, request.delay, request.background_volume_shift)
            except Exception:
                break
            finally:
                time.sleep(0.10)
        logger.debug('Player stopped')
    
    def _play(self, primary, background = None, delay = 2.5, background_volume_shift = 20):
        ''' Play a primary track, with optional background track. If a background track 
        is supplied, it will be started first and the primary track will be started after 
        the delay period has expired.
        
        Arguments:
            primary (str): path to the audio file to use as the primary track
            background (str): path the audio file to use as the background track. Background 
                tracks are played in a loop until the primary track finishes.
            delay (int): amount of time, in seconds, to wait after starting the background 
                track before starting the primary track.
            background_volume_shift (int): amount of volume decrease that should be used for the 
                background track                    
        '''
        self._primary = AudioPlayer(primary)
        self._primary.volume = self._volume
        if background:
            logger.debug(f'Playing background track: {background}')
            self._background = AudioPlayer(background)
            self._background.volume = self._volume - background_volume_shift
            self._background.play(loop = True)
            time.sleep(delay)
        logger.debug(f'Playing primary track: {primary}')            
        self._primary.play(block = True)
        self._stop_playback()
        
    def _stop_playback(self, delay = 2.5):
        ''' Stop the current play request.
        
        Arguments:
            delay (int): amount of time in seconds to wait before stopping the background track
        '''
        if self._primary:
            logger.debug('Stopping primary track')
            self._primary.stop()
            self._primary.close()
        if self._background:
            time.sleep(delay)
            logger.debug('Stopping background track')
            # Fade out the background volume
            while self._background.volume > 0:
                self._background.volume -= 0.5
                time.sleep(0.10)
            self._background.stop()
            self._background.close()
        self._primary = None
        self._background = None    
        
        
class AudioService(BaseService):
    ''' Provides access to audio service operations.
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
    ''' 
    def __init__(self, conductor):
        super().__init__(conductor, 'audio')
        self._queue = deque()
        self._player = None
        
    def shutdown(self):
        ''' Clear the play queue and stop the player. '''
        self._queue.clear()
        if self._player and self._player.is_alive():
            self._player.stop()
        
    def play(self, request):
        ''' Play the supplied request
        
        Adds the supplied request to the play queue and starts the 
        player, if it's not already running.
        
        Arguments:
            request (PlayRequest): request to play
        '''
        self._queue.append(request)
        if not self._player or not self._player.is_alive():
            self._player = Player(self)
            self._player.start()
