class Station:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.enter = []
        self.depart = []
        self.potentialCapacity = capacity
        self.finishedTrains = []
        self.previousStation = ""
