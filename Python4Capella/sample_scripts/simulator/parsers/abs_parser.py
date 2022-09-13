from abc import ABC

class AbstractParser(ABC):
    """
      Abstração de um parser
    """

    def session(self):
        # abstract
        pass

    def state(self):
        # abstract
        pass
