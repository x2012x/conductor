'''
Created on Dec 27, 2020

@author: x2012x
'''
import argparse
from handlers.administration import AdministrationHandler
from handlers.audio import AudioHandler
from handlers.calendar import CalendarHandler
from handlers.routines import RoutinesHandler
from handlers.state import StateHandler
from handlers.tts import TextToSpeechHandler
from services.audio import AudioService
from services.calendar import CalendarService
from services.routines import RoutinesService
from services.state import StateService
from services.tts import TextToSpeechService
from servers.http import Conductor


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Conductor for home automation tasks')
    parser.add_argument('address', type=str, help='IP address to bind to')
    parser.add_argument('port', type=int, help='Port to listen on')
    args = parser.parse_args()
    server = Conductor((args.address, args.port),
                       (AudioService, CalendarService, RoutinesService, StateService, TextToSpeechService), 
                       (AdministrationHandler, StateHandler, CalendarHandler, RoutinesHandler, AudioHandler, TextToSpeechHandler))
    server.serve_forever()
    # TODO: Get rid of prints and add a logger.
    print('Conductor shutdown')
