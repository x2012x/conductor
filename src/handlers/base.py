'''
Created on Dec 30, 2020

@author: x2012x
'''
import logging
from urllib.parse import parse_qs
from inspect import signature, Parameter
from errors.exceptions import UnsupportedAction, SpeakableException
from abc import abstractmethod, ABC
from services.base import Response

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    '''
    Base class that all Handlers should be derived from.
    
    Handlers are responsible for processing intents and also HTTP actions.
    All handlers define their intent processing logic by implementing the _handle_intent(intent) method.
    The processing of HTTP actions is done automatically by this base class by way of mapping the requested 
    action to a method signature on the handler. 
    
    Arguments:
        conductor (Conductor): reference to the running Conductor instance.
        base_path (str): the base URL path that this is registered to handle actions.
        intents ({str}): a set of intent names that this is registered to handle.   
    '''  
    def __init__(self, conductor, base_path, intents={}):
        self.conductor = conductor
        self.base_path = base_path
        self.intents = intents

    def _convert_param(self, param):
        ''' Infer the parameter data type and return the converted value '''
        # Assume the param has already been converted, if not a string
        if not isinstance(param, str):
            return param
        # Attempt integer conversion
        try:
            return int(param)
        except:
            logger.debug(f'Cannot convert {param} to int')
        # Attempt float conversion
        try:
            return float(param)
        except:
            logger.debug(f'Cannot convert {param} to float')
        # Attempt boolean conversion
        TRUE = 'true'
        FALSE = 'false'
        param_lower = param.lower()
        if param_lower in [TRUE, FALSE]:
            return param_lower == TRUE
        # No conversion possible, return unconverted
        return param
        
    def handle_action(self, action, request):
        ''' Process a requested action
        
        Action names should map to methods on the implementing class. The request 
        object will be examined to map request params to method arguments.
        
        Arguments:
            action (str): name of the action to execute, this must map to a method on the action.
            request: urlparse result from conductor pre-processing of the HTTP request.
            
        Returns:
            response: The final response object returned from conductor response processing.            
        '''
        if hasattr(self, action):
            response = Response()
            try:
                # Handlers only support single value query parameters.
                query = {k : self._convert_param(v[0]) for k, v in parse_qs(request.query).items()}
                method = getattr(self, action)
                uses_kwargs = False
                # Process query params to positional method args.
                args = []
                for param in signature(method).parameters.values():
                    # Track if the target method supports variable kwargs
                    if param.kind == Parameter.VAR_KEYWORD:
                        uses_kwargs = True
                    else:
                        # If an argument has a default value and it is not specified in the query parameters, use the default.
                        args.append(param.default if param.name not in query and param.default != Parameter.empty else query.pop(param.name))
                if uses_kwargs:
                    logger.debug(f'Invoking action {action} with args {args} and kwargs {query}')
                    response = method(*args, **query)
                else:
                    logger.debug(f'Invoking action {action} with args {args}')
                    response = method(*args)
            except SpeakableException as e:
                response.speech.text = e.phrase
            return self.conductor.process_response(response)
        else:
            raise UnsupportedAction(f'Unknown action: /{self.base_path}/{action}')
        
    def handle_intent(self, intent):
        ''' Process a received intent
        
        Passes the supplied intent to the implementing class's _handle_intent(intent) method for processing.
        
        Arguments:
            intent (json): JSON intent structure extracted by the conductor from the request payload.
            
        Returns:
            response: The final response object returned from conductor response processing.            
        '''        
        response = Response()
        try:
            response = self._handle_intent(intent)
        except SpeakableException as e:
            response.speech.text = e.phrase
        return self.conductor.process_response(response) 

    @abstractmethod
    def _handle_intent(self, intent):
        ''' Implementing class's intent processing logic
        
        Arguments:
            intent (json): JSON intent structure extracted by the conductor from the request payload.
        '''
        pass
