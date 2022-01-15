class Station:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.enter = []
        self.depart = []
        self.potentialCapacity = capacity
        self.finishedTrains = []
        self.previousStation = ""

    def __repr__(self):
        return self.id

    def placeTrain(self):
        self.capacity -= 1
        self.potentialCapacity -= 1

    def scheduleTrainDepart(self, train):
        self.potentialCapacity += 1
        self.depart.append(train)

    def removeTrainFromDepartSchedule(self, train, stop):
        if stop:
            self.potentialCapacity -= 1
        self.depart.remove(train)

    def scheduleTrainEnter(self, train):
        self.potentialCapacity -= 1
        self.enter.append(train)

    def remTrainEnterSchedule(self, train, stop):
        if stop:
            self.potentialCapacity += 1
        self.enter.remove(train)
