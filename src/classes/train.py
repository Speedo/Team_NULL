from classes.action import Action


class Train:
    def __init__(self, id, startingPosition, speed, capacity, idletime):
        self.id = id
        self.startingPosition = startingPosition
        self.currentStation = None
        self.nextStation = None
        self.boardedPassengers = []
        self.speed = speed
        self.capacity = capacity
        self.actions = []
        self.line = None
        self.progress = 0
        self.timeNeeded = 0
        self.endStation = None
        self.path = []
        self.passengers = []
        self.idle = idletime
        self.isFinished = False
        self.wasFinished = False
        self.potentialLine = None

    def __repr__(self):
        return self.id

    def addAction(self, time, action, target):
        self.actions.append(Action(time, action, target))

    def write(self):
        output = ""
        output += f"[Train:{self.id}]\n"
        for action in self.actions:
            output += action.toString()
        output += "\n"
        return output

    def addStationToPath(self, station):
        self.path.append(self.currentStation.id)
        self.path.append(station.id)
        self.passengers += [[], []]
        self.nextStation = station

    def enableFinishedTrain(self):
        self.isFinished = False
        self.wasFinished = True

    def disableFinishedTrain(self, station):
        self.isFinished = True
        self.wasFinished = False
        station.finishedTrains.append(self)
        # set finished Trains as function in station

    def swapWithTrain(self, train, line):
        # union with push
        self.currentStation.scheduleTrainDepart(self)
        self.addStationToPath(train.currentStation)
        self.enableFinishedTrain()
        train.currentStation.scheduleTrainEnter(self)
        self.potentialLine = line

    def pushTrainToStation(self, station, line):
        # union with swap
        self.currentStation.scheduleTrainDepart(self)
        self.addStationToPath(station)
        self.enableFinishedTrain()
        station.scheduleTrainEnter(self)
        self.potentialLine = line

    def setFinished(self):
        self.isFinished = True
        self.path = []
        self.passengers = []
        self.currentStation.finishedTrains.append(self)
        # set finished Trains as function in station

    def stop(self):
        self.currentStation.removeTrainFromDepartSchedule(self, True)
        self.nextStation.remTrainEnterSchedule(self, True)
        self.nextStation = None
        self.potentialLine.removeTrain()
        self.potentialLine = None

        if self.wasFinished:
            self.disableFinishedTrain(self.currentStation)

    def drive(self):
        self.currentStation.removeTrainFromDepartSchedule(self, False)
        self.nextStation.remTrainEnterSchedule(self, False)
        self.line = self.potentialLine
        self.nextStation.capacity -= 1
        self.currentStation = None
        self.nextStation = None
        self.potentialLine = None
