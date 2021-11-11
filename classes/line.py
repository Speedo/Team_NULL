class Line:
    def __init__(self, id, capacity, length):
        self.id = id
        self.capacity = capacity
        self.length = length
        self.stations = []
        self.trains = []

    def addStation(self, station):
        self.stations.append(station)

    def toString(self):
        return f"ID: {self.id}, capacity: {self.capacity}, length: {self.length}, stations: {self.stations}"