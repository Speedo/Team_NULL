class Line:
    def __init__(self, id, stationA, stationB, length, capacity):
        self.id = id
        self.stations = []
        self.stations.append(stationA)
        self.stations.append(stationB)
        self.length = length
        self.capacity = capacity

    def __repr__(self):
        return self.id

    def addTrain(self):
        self.capacity -= 1

    def removeTrain(self):
        self.capacity += 1
