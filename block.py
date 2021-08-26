from data import Data


class Block:
    def __init__(self, data: Data):
        self.data = data

        self.init()

    def init(self):
        pass

    def clock_up(self):
        pass

    def clock_down(self):
        pass
