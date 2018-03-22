import curses
from curses.textpad import Textbox


CURRENT_WINDOW = None 


class FileService:
    @staticmethod
    def to_list(path):
        import os
        return list(os.listdir(path))
        raise Exception(os.listdir(path))

class CommandEvent:
    def __init__(self, command):
        self.command = command

class ChangeContentProviderEvent:
    def __init__(self, service, extra):
        self.service = service
        self.extra = extra

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
            if event.command.startswith('file'):
                command = event.command[4:]
                command = command.lstrip()
                EVENT_DISPATCHER.listen(ChangeContentProviderEvent(FileService, command))
                

class EventDispatcher(EventListener):
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def listen(self, event):
        for x in self.listeners:
            x.listen(event)

class ListWin(EventListener):
    def __init__(self, window, subpad):
        self.win = window
        self.win.border()
        self.win.refresh()
        self.subpad = subpad
        self.current_element = None
        self.current_service = None
        self.current_extra = None
        self.__current_index = 0

    @property
    def current_index(self):
        return self.__current_index

    def decrease_index(self):
        self.__current_index = min(len(self.content) -1,
                                   max(self.__current_index - 1 , 0))
        if self.content:
            self.current_element = self.content[self.__current_index]

    def increase_index(self):
        self.__current_index = min(self.__current_index +1 , len(self.content) - 1)
        if self.content:
            self.current_element = self.content[self.__current_index]

    @property
    def content(self):
        try:
            return self.current_service.to_list(self.current_extra)
        except AttributeError:
            return []

    def listen(self, event):
        if isinstance(event, ChangeContentProviderEvent):
            self.current_service = event.service
            self.current_extra = event.extra
            self.win.erase()
            self.win.border()
            self.refresh()

    def refresh(self):
        win_y, win_x = self.win.getmaxyx()
        self.subpad.resize(max(len(self.content), 1),
                           max(win_x - 1, 1))
        for index, element in enumerate(self.content):
            self.subpad.move(index, 1)
            attributes = 0
            if element == self.current_element:
                attributes |= curses.A_BOLD
            if index == self.current_index:
                attributes |= curses.A_BLINK
            self.subpad.addstr(element, attributes)
        self.win.refresh()
        self.win.border()
        self.subpad.refresh(0, 0, 3, 1, win_y - 1, win_x - 1)

    def submit_change(self):
        import os.path
        EVENT_DISPATCHER.listen(ChangeContentProviderEvent(self.current_service,
                                                           os.path.join(self.current_extra,
                                                                        self.current_element)))

EVENT_DISPATCHER = EventDispatcher()

class CommandWindow(EventListener):
    def __init__(self, textbox):
        self.textbox = textbox
        self.win = textbox.win
        self.refresh()

    def refresh(self):
        self.win.move(0,0)
        if CURRENT_WINDOW is self:
            self.win.addstr('$', curses.color_pair(2))
        self.win.refresh()

    def submit_command(self, last_command):
        last_command = last_command.lstrip('$').rstrip()
        EVENT_DISPATCHER.listen(CommandEvent(last_command))
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
    max_y, max_x = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
    topic_bar = TopicWindow(curses.newwin(2, max_x))
    list_win = ListWin(curses.newwin(max_y-2, max_x, 1, 0), curses.newpad(20, 20))
    textwin = curses.newwin(1, max_x, max_y-1, 0)
    textbox = Textbox(textwin)
    command_win = CommandWindow(textbox)
    global CURRENT_WINDOW, EVENT_DISPATCHER
    supervisor = Supervisor()
    EVENT_DISPATCHER.register(topic_bar)
    EVENT_DISPATCHER.register(supervisor)
    EVENT_DISPATCHER.register(list_win)
    def resize_windows(new_y, new_x):
        topic_bar.win.resize(2, new_x)
        topic_bar.win.redrawwin()
        topic_bar.win.refresh()
        list_win.win.resize(new_y-2, new_x)
        list_win.win.redrawwin()
        list_win.win.refresh()
        textwin.resize(1, new_x)
        textwin.mvwin(new_y-1, 0)
        textwin.redrawwin()
        textwin.refresh()

    
    while not supervisor.exit:
        if curses.is_term_resized(max_y, max_x):
            max_y, max_x = stdscr.getmaxyx()
            resize_windows(max_y, max_x)
        if CURRENT_WINDOW == command_win:
            command = command_win.textbox.edit()
            command_win.submit_command(command)
            CURRENT_WINDOW = list_win
            continue
        c = textwin.getch()
        if c == curses.KEY_UP:
            CURRENT_WINDOW = list_win
            list_win.decrease_index()
        elif c == curses.KEY_DOWN:
            CURRENT_WINDOW = list_win
            list_win.increase_index()
        elif c == 27:
            CURRENT_WINDOW = command_win
            command_win.refresh()
        elif c in (curses.KEY_ENTER, 10):
            if CURRENT_WINDOW == list_win:
                list_win.submit_change()
        list_win.refresh()

if __name__ == "__main__":
    try:
        mainloop()
    finally:
        curses.endwin()
