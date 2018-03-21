import curses
from curses.textpad import Textbox


CURRENT_WINDOW = None 


class CommandEvent:
    def __init__(self, command):
        self.command = command

class EventListener:
    def listen(self, event):
        return

class Supervisor(EventListener):
    def __init__(self):
        self.exit = False

    def listen(self, event):
        if isinstance(event, CommandEvent):
            if event.command == ':q':
                self.exit = True

class EventDispatcher(EventListener):
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def listen(self, event):
        for x in self.listeners:
            x.listen(event)

class ListWin(EventListener):
    def __init__(self, window):
        self.win = window
        self.win.border()
        self.win.refresh()
        self.current_element = None
        self.__current_index = 0
        self.content = []

    @property
    def current_index(self):
        return self.__current_index

    def decrease_index(self):
        self.__current_index = max(self.__current_index - 1 , 0)

    def increase_index(self):
        self.__current_index = min(self.__current_index +1 , len(self.content) - 1)

    def load_list(self, iterable):
        self.win.border()
        self.content = iterable

    def refresh(self):
        for index, element in enumerate(self.content):
            self.win.move(index + 1, 1)
            attributes = 0
            if element == self.current_element:
                attributes |= curses.A_BOLD
            if index == self.current_index:
                attributes |= curses.A_BLINK
            self.win.addstr(element, attributes)
        self.win.refresh()

EVENT_DISPATCHER = EventDispatcher()

class CommandWindow(EventListener):
    def __init__(self, textbox):
        self.textbox = textbox
        self.win = textbox.win
        self.last_command = ''
        self.refresh()

    def refresh(self):
        self.win.move(0,0)
        if CURRENT_WINDOW is self:
            self.win.addstr('$', curses.color_pair(2))
        self.win.addstr(self.last_command)
        self.win.refresh()

    def addchr(self, char):
        self.last_command += char
        self.refresh()

    def submit_command(self):
        EVENT_DISPATCHER.listen(CommandEvent(self.last_command))
        self.last_command = ''
        self.win.erase()

class TopicWindow(EventListener):
    def __init__(self, window):
        self.win = window
        self.win.move(0, 1)
        self.win.addstr('TOPIC', curses.color_pair(1))
        self.refresh()

    def refresh(self):
        self.win.refresh()

    def listen(self, event):
        if isinstance(event, CommandEvent):
            self.win.addstr(event.command)
            self.refresh()


def mainloop():
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
    topic_bar = TopicWindow(curses.newwin(2, 80))
    list_win = ListWin(curses.newwin(21, 40, 1, 0))
    textwin = curses.newwin(3, 80, 22, 0)
    textbox = Textbox(textwin)
    command_win = CommandWindow(textbox)
    global CURRENT_WINDOW, EVENT_DISPATCHER
    EVENT_DISPATCHER.register(topic_bar)
    supervisor = Supervisor()
    EVENT_DISPATCHER.register(supervisor)
    
    while True:
        if supervisor.exit:
            break
        c = textwin.getch()
        if c == ord('p'):
            list_win.load_list(["blabla", "blabla2"])
        elif c == curses.KEY_UP:
            CURRENT_WINDOW = list_win
            list_win.decrease_index()
        elif c == curses.KEY_DOWN:
            CURRENT_WINDOW = list_win
            list_win.increase_index()
        elif c == 27:
            CURRENT_WINDOW = command_win
            command_win.refresh()
        elif c in (curses.KEY_ENTER, 10):
            command_win.submit_command()
            CURRENT_WINDOW = list_win
        elif CURRENT_WINDOW == command_win:
            command_win.addchr(chr(c))
        list_win.refresh()

if __name__ == "__main__":
    try:
        mainloop()
    finally:
        curses.endwin()
