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

