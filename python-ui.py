from events import (CommandEvent, CommandError, InvalidURLServiceError,
                    RequestChangeURLServiceEvent, ChangedURLServiceEvent,
                    EventListener, EVENT_DISPATCHER)

from supervisor import Supervisor

class ListQuery(EventListener):
    def __init__(self):
        self.current_service = None
        self.current_url = None
        self.__current_index = 0

    @property
    def current_index(self):
        if not self.content:
            return 0
        return max(0, min(self.__current_index, len(self.content) - 1))

    @property
    def current_element(self):
        try:
            return self.content[self.current_index]
        except IndexError:
            raise AttributeError

    def decrease_index(self, amount=1):
        previous_index = self.__current_index
        self.__current_index = min(len(self.content) - 1,
                                   max(self.__current_index - amount , 0))

    def increase_index(self, amount=1):
        previous_index = self.__current_index
        self.__current_index = min(self.__current_index + amount,
                                   len(self.content) - 1)

    @property
    def content(self):
        try:
            return self.current_service.to_element_list(self.current_url)
        except AttributeError:
            return []

    def listen(self, event):
        if isinstance(event, RequestChangeURLServiceEvent):
            if not event.service.test_url(event.url):
                EVENT_DISPATCHER.listen(InvalidURLServiceError(event))
                return
            self.current_service = event.service
            self.current_url = event.url



class Commander(EventListener):
    def submit_command(self, last_command):
        last_command = last_command.lstrip('$').rstrip()
        EVENT_DISPATCHER.listen(CommandEvent(last_command))

    def listen(self, event):
        if isinstance(event, InvalidURLServiceError):
            url_str = str(event.event.url)
            service_str = str(event.event.service)
        elif isinstance(event, CommandError):
            pass

def list_value_and_commander_factory():
    new_list = ListQuery()
    global CURRENT_WINDOW, EVENT_DISPATCHER
    supervisor = Supervisor()
    commander = Commander()
    EVENT_DISPATCHER.register(new_list)
    EVENT_DISPATCHER.register(commander)
    EVENT_DISPATCHER.register(supervisor)
    return new_list, commander



if __name__ == "__main__":
    list_value, commander = list_value_and_commander_factory()
    commander.submit_command('dir /')
    from pprint import pprint
    pprint(list_value.content)
    commander.submit_command('dir /tmp')
    pprint(list_value.content)
    pprint(list_value.current_element)

    
