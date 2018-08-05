class CommandEvent:
    def __init__(self, command):
        self.command = command

class CommandError:
    def __init__(self, event):
        self.event = event

class InvalidURLServiceError:
    def __init__(self, event):
        self.event = event

class RequestChangeURLServiceEvent:
    def __init__(self, service, url):
        self.service = service
        self.url = url

class ChangedURLServiceEvent:
    def __init__(self, service, url):
        self.service = service
        self.url = url


class EventListener:
    def listen(self, event):
        return

class EventDispatcher(EventListener):
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def listen(self, event):
        for x in self.listeners:
            x.listen(event)

EVENT_DISPATCHER = EventDispatcher()
