import enum


class Status(enum.IntEnum):
    """
    Class with enums for our component status
    """

    Waiting = 0
    Working = 1
    Error = 2
