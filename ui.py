import curses
from curses.textpad import Textbox, rectangle

class ListWin:
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



def mainloop():
    stdscr = curses.initscr()
    topic_bar = curses.newwin(2, 80)
    topic_bar.border()
    topic_bar.move(0, 1)
    topic_bar.addstr('TOPIC')
    topic_bar.refresh()
    win = curses.newwin(21, 40, 1, 0)
    list_win = ListWin(win)
    textwin = curses.newwin(3, 80, 21, 0)
    textbox = Textbox(textwin)
    last_command = ''
    while True:
        c = textwin.getch()
        if c == ord('p'):
            list_win.load_list(["blabla", "blabla2"])
        elif c == curses.KEY_UP:
            list_win.decrease_index()
        elif c == curses.KEY_DOWN:
            list_win.increase_index()
        elif c == ord('q'):
            break  # Exit the while loop
        elif c in (curses.KEY_ENTER, 10):
            topic_bar.addstr(last_command)
            topic_bar.refresh()
            last_command = ''
        else:
            last_command += chr(c)
        list_win.refresh()

if __name__ == "__main__":
    try:
        mainloop()
    finally:
        curses.endwin()
