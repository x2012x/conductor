'''
Created on Jun 24, 2021

@author: x2012x
'''
import traceback
import json
import logging
from collections.abc import Iterable
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from errors.exceptions import UnsupportedAction, RegistrationExists,\
    UnsupportedIntent, SpeakableException
from errors.reasons import get_reason
from services.base import Response

logger = logging.getLogger(__name__)

# Prefer the ThreadingHTTPServer but fallback on HTTPServer if unavailable.
try:
    from http.server import ThreadingHTTPServer as ServerImpl 
except Exception:
    from http.server import HTTPServer as ServerImpl 


class Conductor(ServerImpl):
    '''
    Conductor HTTP Server
    
    The primary responsibility of the Conductor is to receive HTTP requests and delegate to the appropriate handler.
    Additionally, services should be assigned as distinct attributes to the Conductor during instantiation.
    
    Arguments:
        server_address ((str,int)): tuple representing the IP and Port to listen on.
        services ([BaseService]): collection of class definitions all derived from BaseService.
        handlers ([BaseHandler]): collection of class definitions all derived from BaseHandler.
    '''    
    def __init__(self, server_address, services, handlers):
        super().__init__(server_address, RequestHandler)
        # Keep track of registered service names
        self.services = set()
        # Register all services
        for service in services:
            self.register_service(service(self))
        # Map of registered handlers
        self.handlers = {}
        for handler in handlers:
            self.register_handler(handler(self))
        # Tracks the last collection of responses that were processed.
        self.last_response = None
        
    def shutdown(self):
        '''Shutdown the Conductor HTTP service'''
        # Shutdown all services before shutting down the Conductor
        for service in self.services:
            if hasattr(self, service):
                getattr(self, service).shutdown()
        super().shutdown()

    def register_service(self, service):
        ''' Register the supplied service with the conductor

        Arguments:
            service (BaseService): an object derived from BaseService.        
        '''
        logger.debug(f'Registering Service: {service.name}')
        if hasattr(self, service.name):
            raise RegistrationExists(f'Service already registered: {service.name}')
        setattr(self, service.name, service)
        self.services.add(service.name)

    def register_handler(self, handler):
        ''' Register the supplied handler with the conductor

        Arguments:
            handler (BaseHandler): an object derived from BaseHandler.        
        '''
        logger.debug(f'Registering Handler Path: {handler.base_path}')
        if handler.base_path in self.handlers:
            raise RegistrationExists(f'Path already registered: {handler.base_path}')
        self.handlers[handler.base_path] = handler
        for intent in handler.intents:
            logger.debug(f'Registering Handler Intent: {intent}')
            if intent in self.handlers:
                raise RegistrationExists(f'Intent already registered: {intent}')
            self.handlers[intent] = handler
            
    def process_response(self, response):
        ''' Process the raw handler's response to construct a final response.
        
        Arguments:
            response (Response): Raw response from a handler. This could be no response, a single 
                Response instance or a collection of Response instances.
                
        Returns:
            response: The final response object used to build the a response body the requestor.        
        '''
        server_response = Response()
        # If the handler didn't supply a response, create one.
        if not response:
            response = Response()
        # Ensure we have a collection of responses to process, even if only one was supplied to process.
        responses = response if isinstance(response, Iterable) else [response]
        response_phrase = ''
        exception = None
        # Track these responses as the last collection of responses processed.
        self.last_response = responses
        # Process all of the responses
        for r in responses:
            if r.speech.text:
                try:
                    self.tts.speak_response(r)
                except SpeakableException as e:
                    # For now, we are only going to keep track of the last reported exception. This needs improved.
                    exception = e
                    response_phrase += f'{e.phrase} '
        # If a SpeakableException was reported, return the entire string of response phrases, with a reason.
        if exception:
            response_phrase = f'{response_phrase} Sorry I sound odd, {get_reason(exception)}'
        server_response.speech.text = response_phrase
        return server_response
            

class RequestHandler(BaseHTTPRequestHandler):
    ''' 
    The base HTTP handler used by the Conductor to process HTTP requests.
    
    This base handler will receive an HTTP request and determine which registered handler 
    to delegate to based on the intent that was received or HTTP path called.
    '''
    def log_message(self, format, *args):
        pass
    
    def _send_success(self):
        self.send_response(200)
        self.end_headers()
        
    def _send_unknown_req(self):
        self.send_response(400)
        self.end_headers()
        
    def _send_server_error(self):
        self.send_response(500)
        self.end_headers()

    def do_POST(self):
        intent = None
        # If the path posted to was the 'intent' path, parse the intent JSON and pass the intent along for further processing.
        if self.path.endswith('intent'):
            intent = json.loads(self.rfile.read(int(self.headers['content-length'])))
        self._process_request(intent)

    def do_PUT(self):        
        self._process_request()
        
    def do_GET(self):        
        self._process_request()
            
    def _process_request(self, intent=None):
        ''' Process the current request either by handling the supplied intent or requested path '''
        try:
            if intent:
                logger.info(f'Processing intent: {intent}')
                # Locate the handler registered for this intent name and pass the intent to it for processing.
                intent_name = intent['intent']['name']
                if intent_name in self.server.handlers:
                    response = self.server.handlers[intent_name].handle_intent(intent)
                else:
                    raise UnsupportedIntent(f'Unkown intent: {intent_name}')
            # If an intent wasn't supplied, see if a handler is registered to process the path.
            else:
                logger.info(f'Processing path: {self.path}')
                parsed_path = urlparse(self.path)
                path_components = parsed_path.path.split('/')            
                if len(path_components) > 2 and path_components[1] in self.server.handlers:
                    response = self.server.handlers[path_components[1]].handle_action(path_components[2], parsed_path)
                else:
                    raise UnsupportedAction(f'Unknown path: {parsed_path.path}')
            logger.info(f'Sending response: {response.toJSON()}')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Respond to the requestor with the response object in JSON format.
            self.wfile.write(response.toJSON().encode("utf_8"))
        except UnsupportedAction:
            logger.error(f'Unsupported action: {self.path}\n{traceback.format_exc()}')
            self._send_unknown_req()
        except UnsupportedIntent:
            logger.error(f'Unsupported intent: {intent}\n{traceback.format_exc()}')
            self._send_unknown_req()
        except Exception:
            logger.error(f'Error processing request: {self.path}\n{traceback.format_exc()}')
            self._send_server_error()
