# Conductor

The Conductor is a Python HTTP service that enables developers to register Handlers for processing Intents received from [Rhasspy](https://github.com/rhasspy/rhasspy). In addition to Rhasspy Intent processing, Handlers are also registered to process basic HTTP requests. I originally built the Conductor for several personal home automation projects (e.g. [Hogwarts Assistant](https://youtube.com/playlist?list=PL9hIL6rjAWbK441tUN5FHKqS294GY1i_7)) and have decided to share the framework for others to use.

## Built-Ins
There are a few built-in Handlers & Services provided with the base project but the expectation is that developers will create new ones to meet their project's specific needs. Some basic [examples](examples) are also provided for reference purposes.

**Handlers**
- Administration
- Audio
- Calendar
- Routines
- State
- TTS

**Services**
- Audio
- Calendar
- Routines
- State
- TTS

## Request Handling
When the Conductor receives an HTTP request, it will delegate to the registered Handler or return an HTTP error code if no Handler exists. Before returning the results of the HTTP request, the Conductor will process any Response objects received from the executed Handler. If any of the Response objects define speech text, the Conductor will automatically attempt to speak the text using the TTS service. If the TTS service cannot process the request, the speech text will be returned in the HTTP response object for the requesting client to handle as they see fit.

## Getting Started

**Required Libraries**
* See the [Pipfile](Pipfile) for library requirements.
* **NOTE:** The Conductor's TTS service relies on Google's [Text-To-Speech](https://cloud.google.com/text-to-speech) API and expects your Google API service account JSON file to be located at ['resources/config/google-tts.json'](src/resources/config/README.txt). The Conductor will fail to launch if this file is not present. If you would rather not use Google's TTS API, you'll have to swap out the TextToSpeechService class in ['services/tts.py'](src/services/tts.py) with another implementation.
* In an attempt to reduce the number of Google TTS API calls, a cache of previously processed phrases is maintained at 'resources/cache/tts_cache'. In the future, I plan to add a scheduler service into the Conductor which will be leveraged to remove old cache entries but for now you'll need to manually maintain the cache to prevent it from growing uncontrolled (e.g. a CRON job to delete old files would do the trick).

**Configuration**

Configuration is managed by the [configuration.py](src/utils/configuration.py) module and is backed by two yaml files in the ['resources/config'](src/resources/config) directory. To access configuration, simply import `config` from the module and access properties by key, see below.

```python
from utils.configuration import config

config['application']['LIFX']['url']
config['protected']['LIFX']['api_token']
```

* [application.yaml](src/resources/config/application.yaml)
    * General application settings.
    * Settings you don't mind being tracked by source control.
* [protected.yaml](src/resources/config/protected.yaml.example)
    * While not required, it is recommended to use this file for configuration that shouldn't be tracked by source control such as tokens, credentials and other sensitive information.
    * Create a copy, minus the .example extension, if you'd like to make use of the protected config.
    * The `protected.yaml` file is defined in [.gitignore](.gitignore) to prevent tracking. 

**Running the Conductor**

The Conductor service can be launched at the command-line via:

<code>python conductor.py [IP] [PORT]</code>

For instance, if you wanted to bind to all IP interfaces and listen on port 8080.

<code>python conductor.py 0.0.0.0 8080</code>

I typically setup the Conductor to run as a systemd service on my Raspberry Pi devices, see the example [conductor.service](examples/conductor.service) file.

**Handlers & Services**

To make the Conductor do something meaningful, you'll need to define Handlers and Services to perform those operations.

* Rhasspy's Intent Handling configuration should be setup for 'Remote HTTP' with the 'Remote URL' pointing to the Conductor's intent path (e.g. http://127.0.0.1:8080/intent)

* To get familiar with how Handlers and Services are defined, I recommend examining some of the built-in Handlers and Services. For instance, the built-in Calendar [service](src/services/calendar.py) & [handler](src/handlers/calendar.py) provides simple operations to get the current day/time info and should serve as a good example of how to define a basic Handler and Service.

    * For instance, the Calendar Handler provides access to the current time for:
       * Rhasspy: **CalendarCurrentTime** Intents.
       * HTTP GETs: Get requests to path '/calendar/current_time'

* See the [examples](examples) directory for samples of how to define Handlers and Services to do more interesting operations, such as interacting with [LIFX lights](examples/lights.py).


