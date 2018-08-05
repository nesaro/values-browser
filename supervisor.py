from collections import namedtuple
from services import DirectoryListService, HistoryService, GuessService
from events import (CommandEvent, CommandError, 
                    RequestChangeURLServiceEvent, ChangedURLServiceEvent,
                    EventListener, EVENT_DISPATCHER)

CONTENT_HISTORY = []
HISTORY_SERVICE = HistoryService(CONTENT_HISTORY)

HistoryElement = namedtuple('HistoryElement', ['service', 'url'])

class Supervisor(EventListener):
    def __init__(self):
        self.exit = False

    def listen(self, event):
        if isinstance(event, CommandEvent):
            if event.command == ':q':
                self.exit = True
            if event.command.startswith('dir'):
                url = event.command[4:]
                url = url.lstrip()
                url = "file://" + url
                EVENT_DISPATCHER.listen(RequestChangeURLServiceEvent(DirectoryListService, url))
            elif event.command.startswith('log'):
                url = "log://" 
                EVENT_DISPATCHER.listen(RequestChangeURLServiceEvent(HISTORY_SERVICE, url))
            elif event.command.startswith('guess'):
                url = event.command[6:]
                url = url.lstrip()
                EVENT_DISPATCHER.listen(RequestChangeURLServiceEvent(GuessService, url))
            else:
                EVENT_DISPATCHER.listen(CommandError(event))
        if isinstance(event, ChangedURLServiceEvent):
            global CONTENT_HISTORY
            CONTENT_HISTORY.append(HistoryElement(event.service, event.url))
                
