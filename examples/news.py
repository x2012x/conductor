'''
Created on Apr 25, 2021

@author: x2012x
'''
import os
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from services.base import BaseService, Response
from errors.reasons import get_general_failure
from services.audio import PlayRequest
from handlers.base import BaseHandler
from errors.exceptions import SpeakableException

# Intents
NEWS_LATEST = 'NewsLatest'


class NewsFailure(SpeakableException):
    pass


class NewsHandler(BaseHandler):
    
    def __init__(self, conductor):
        super().__init__(conductor, 'news', {NEWS_LATEST})
        
    def latest(self):
        return self.conductor.news.latest()

    def _handle_intent(self, intent):
        if intent['intent']['name'] == NEWS_LATEST:
            return self.latest()


class NewsService(BaseService):
    ''' Service that plays the latest hourly NPR news feed '''

    def __init__(self, conductor):
        super().__init__(conductor, 'news')
        self._feed = 'https://feeds.npr.org/500005/podcast.xml'
        self._timeout = 3.00
        self._cache = 'resources/cache/news_cache'
        Path(self._cache).mkdir(parents=True, exist_ok=True)
        
    def _fetch_latest(self):
        root = ET.fromstring(requests.get(self._feed, timeout=self._timeout).content.decode('utf-8'))
        remote_audio = root.find('channel').find('item').find('enclosure').get('url')
        title = root.find('channel').find('item').find('title').text.replace(':','').replace(' ','_')
        latest = os.path.join(self._cache, f'{title}.mp3')
        if not os.path.exists(latest) and remote_audio and title:
            fetched_audio = requests.get(remote_audio, timeout=self._timeout)
            with open(latest, 'wb') as f:
                f.write(fetched_audio.content)
        else:
            print(f'Playing audio from cache {latest}')
        return latest
        
    def latest(self):
        try:
            news_file = self._fetch_latest()
            self.conductor.audio.play(PlayRequest(news_file))
        except Exception:
            raise NewsFailure(get_general_failure())            
        return Response()
