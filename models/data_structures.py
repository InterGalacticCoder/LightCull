from collections import deque


class PhotoQueue:
    """Struktur Data Queue (FIFO) untuk antrean pemindaian foto."""

    def __init__(self):
        self.__items = deque()

    def enqueue(self, item):
        self.__items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.__items.popleft()
        return None

    def peek(self):
        if not self.is_empty():
            return self.__items[0]
        return None

    def is_empty(self) -> bool:
        return len(self.__items) == 0

    def size(self) -> int:
        return len(self.__items)

    def clear(self):
        self.__items.clear()


class UndoStack:
    """Struktur Data Stack (LIFO) untuk fitur Undo pemindahan file."""

    def __init__(self):
        self.__items = []

    def push(self, record: dict):
        self.__items.append(record)

    def pop(self):
        if not self.is_empty():
            return self.__items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.__items[-1]
        return None

    def is_empty(self) -> bool:
        return len(self.__items) == 0

    def size(self) -> int:
        return len(self.__items)

    def clear(self):
        self.__items.clear()