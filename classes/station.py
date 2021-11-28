class Station:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.passengers = []
        self.trains = []

    def addPassenger(self, passenger):
        self.passengers.append(passenger)

    def addTrain(self, train):
        self.trains.append(train)
