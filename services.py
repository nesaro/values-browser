import os
from collections import namedtuple

ListElement = namedtuple('ListElement', ['url', 'display_string'])

class DirectoryListService: #This is a type of list service?
    @staticmethod
    def to_element_list(url):
        path = url[7:]
        list_dir = sorted(list(os.listdir(path)))
        return [ListElement(url="file://" + os.path.join(path, x),
                            display_string=x) for x in list_dir]

    @staticmethod
    def test_url(url):
        if not url.startswith('file://'):
            return False
        path = url[7:]
        return os.path.isdir(path)

class HistoryService:
    def __init__(self, content_history):
        self.content_history = content_history

    def to_element_list(self, _):
        return [ListElement(url=x.url,
                            display_string=x.url) for x in self.content_history]

    @staticmethod
    def test_url(url):
        return url.startswith('log://')


