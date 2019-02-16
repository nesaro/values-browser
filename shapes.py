class ListShape:
    def __init__(self):
        self._current_index = 0

    @property
    def content(self):
        raise NotImplementedError

    @property
    def current_index(self):
        if not self.content:
            return 0
        return max(0, min(self._current_index, len(self.content) - 1))

    @property
    def current_element(self):
        try:
            return self.content[self.current_index]
        except IndexError:
            raise AttributeError

    def decrease_index(self, amount=1):
        previous_index = self._current_index
        self._current_index = min(len(self.content) - 1,
                                  max(self._current_index - amount , 0))

    def increase_index(self, amount=1):
        previous_index = self._current_index
        self._current_index = min(self._current_index + amount,
                                  len(self.content) - 1)

