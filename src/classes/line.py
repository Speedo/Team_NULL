class Line:
    def __init__(self, id, stationA, stationB, length, capacity):
        self.id = id
        self.stations = []
        self.stations.append(stationA)
        self.stations.append(stationB)
        self.length = length
        self.capacity = capacity