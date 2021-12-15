class Line:
    def __init__(self, id, length, capacity):
        self.id = id
        self.capacity = capacity
        self.length = length
        self.stations = []

    def addStation(self, station):
        self.stations.append(station)
