import curses
import curses.panel
from collections import namedtuple
from curses.textpad import Textbox
from services import DirectoryListService, HistoryService, GuessService
from events import (CommandEvent, CommandError, InvalidURLServiceError,
                    RequestChangeURLServiceEvent, ChangedURLServiceEvent,
                    EventListener, EventDispatcher)

HistoryElement = namedtuple('HistoryElement', ['service', 'url'])

CURRENT_WINDOW = None 
CONTENT_HISTORY = []
HISTORY_SERVICE = HistoryService(CONTENT_HISTORY)

#create class to associate URL to content provider
#put the content provider and the url on the topic bar

#Create a context menu for URL (actions) and VALUE (actions)

class URLActionOptions:
    def get_actions(url) -> 'list_of_actions names and services':
        pass

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
                

class ListWin(EventListener):
    def __init__(self, window, subpad):
        self.win = window
        self.panel = curses.panel.new_panel(window)
        self.panel.move(1, 0)
        self.win.border()
        self.win.refresh()
        self.subpad = subpad
        self.current_service = None
        self.current_url = None
        self.__current_index = 0

    @property
    def row_size(self):
        max_y, _ = self.win.getmaxyx()
        return max_y - 2

    @property
    def current_page(self):
        if not self.content:
            return 0
        return self.current_index // self.row_size

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
        try:
            self.__redraw_index(previous_index, self.content[previous_index])
        except IndexError:
            pass
        try:
            current_element = self.current_element
        except AttributeError:
            pass
        else:
            self.__redraw_index(self.__current_index, current_element)

    def increase_index(self, amount=1):
        previous_index = self.__current_index
        self.__current_index = min(self.__current_index + amount,
                                   len(self.content) - 1)
        try:
            self.__redraw_index(previous_index, self.content[previous_index])
        except IndexError:
            pass
        try:
            self.__redraw_index(self.__current_index, self.current_element)
        except AttributeError:
            pass

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
            EVENT_DISPATCHER.listen(ChangedURLServiceEvent(event.service,
                                                           event.url))
            self.redraw()

    def __redraw_index(self, index, element):
        self.subpad.move(index, 1)
        attributes = 0
        if element == self.current_element:
            attributes |= curses.A_BOLD
        if index == self.current_index:
            attributes |= curses.A_BLINK
        self.subpad.addstr(element.display_string, attributes)
        win_y, win_x = self.win.getmaxyx()
        self.subpad.refresh(self.current_page * (win_y - 2) , 0, 2, 1,
                            win_y - 1, win_x - 2)

    def redraw_content(self):
        win_y, win_x = self.win.getmaxyx()
        #TODO if size is smaller, redraw win
        self.subpad.resize(max(len(self.content), 1),
                           max(win_x - 1, 1))
        for index, element in enumerate(self.content):
            self.__redraw_index(index, element)

        self.subpad.refresh(self.current_page * (win_y - 2) , 0, 2, 1,
                            win_y - 1, win_x - 2)

    def redraw(self):
        self.win.border()
        self.win.refresh()
        self.redraw_content()

    def submit_change(self):
        try:
            element = self.current_element
        except AttributeError:
            return
        EVENT_DISPATCHER.listen(RequestChangeURLServiceEvent(element.service,
                                                             element.url))

EVENT_DISPATCHER = EventDispatcher()

class CommandWindow(EventListener):
    def __init__(self, textbox):
        self.textbox = textbox
        self.win = textbox.win
        self.redraw()

    def redraw(self):
        self.win.clear()
        if CURRENT_WINDOW is self:
            self.win.addstr('$', curses.color_pair(2))
        self.win.refresh()

    def submit_command(self, last_command):
        last_command = last_command.lstrip('$').rstrip()
        self.redraw()
        EVENT_DISPATCHER.listen(CommandEvent(last_command))

    def listen(self, event):
        if isinstance(event, InvalidURLServiceError):
            url_str = str(event.event.url)
            service_str = str(event.event.service)
            self.win.move(0, 1)
            self.win.addstr('INVALID URL {} for service {}'.format(url_str,
                                                                   service_str))
            self.win.refresh()
        elif isinstance(event, CommandError):
            self.win.move(0, 1)
            self.win.addstr('INVALID command {}'.format(event.event.command))
            self.win.refresh()

class TopicWindow(EventListener):
    def __init__(self, window):
        self.win = window
        self.win.move(0, 1)
        self.win.addstr('TOPIC', curses.color_pair(1))
        self.win.refresh()

    def listen(self, event):
        if isinstance(event, ChangedURLServiceEvent):
            self.win.clear()
            self.win.addstr(str(event.service) + ' ')
            self.win.addstr(event.url, curses.color_pair(2))
            self.win.refresh()


class HelpWindow:
    def __init__(self, stdscr):
        max_y, max_x = stdscr.getmaxyx()
        self.panel = curses.panel.new_panel(curses.newwin(20, 20, 2, 2))
        self.panel.move(2, 1)

    def display(self):
        win = self.panel.window()
        win.erase()
        win.border()
        lines = (':u  Change URL',
                 ':s  Change Service',
                 ':q  exit')
        for index, line in enumerate(lines):
            win.move(1+index,1)
            win.addstr(line)
        win.refresh()
        self.panel.show()

    def hide(self):
        self.panel.hide()


def mainloop():
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    max_y, max_x = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
    topic_bar = TopicWindow(curses.newwin(2, max_x))
    list_win = ListWin(curses.newwin(max_y - 2, max_x, 1, 0), curses.newpad(20, 20))
    textwin = curses.newwin(1, max_x, max_y-1, 0)
    textbox = Textbox(textwin)
    help_window = HelpWindow(stdscr)
    command_win = CommandWindow(textbox)
    global CURRENT_WINDOW, EVENT_DISPATCHER
    supervisor = Supervisor()
    EVENT_DISPATCHER.register(topic_bar)
    EVENT_DISPATCHER.register(supervisor)
    EVENT_DISPATCHER.register(list_win)
    EVENT_DISPATCHER.register(command_win)
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
            CURRENT_WINDOW = list_win
            command_win.submit_command(command)
            continue
        c = textwin.getch()
        if CURRENT_WINDOW == list_win and c == curses.KEY_UP:
            list_win.decrease_index()
        elif CURRENT_WINDOW == list_win and c == curses.KEY_DOWN:
            list_win.increase_index()
        elif CURRENT_WINDOW == list_win and c == curses.KEY_NPAGE:
            list_win.increase_index(20)
        elif CURRENT_WINDOW == list_win and c == curses.KEY_PPAGE:
            list_win.decrease_index(20)
        elif c == curses.KEY_F1 and CURRENT_WINDOW == help_window:
            help_window.hide()
            list_win.panel.top()
            CURRENT_WINDOW = list_win
            curses.panel.update_panels()
            list_win.redraw_content()
            curses.doupdate()
        elif c == curses.KEY_F1 and CURRENT_WINDOW == list_win:
            help_window.display()
            list_win.panel.bottom()
            CURRENT_WINDOW = help_window
            curses.panel.update_panels()
            curses.doupdate()
        elif c == 27:
            CURRENT_WINDOW = command_win
            command_win.redraw()
        elif c in (curses.KEY_ENTER, 10):
            if CURRENT_WINDOW == list_win:
                list_win.submit_change()

if __name__ == "__main__":
    try:
        mainloop()
    finally:
        curses.endwin()
