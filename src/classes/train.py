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

    def addAction(self, time, action, target):
        self.actions.append(Action(time, action, target))

    def write(self):
        output = ""
        output += f"[Train:{self.id}]\n"
        for action in self.actions:
            output += action.toString()
        output += "\n"
        return output

# Swap Routine
# swapTrain.currentStation.depart.append(swapTrain)
# swapTrain.currentStation.scheduleTrainDepart()
# swapTrain.path.append(swapTrain.currentStation.id)
# swapTrain.path.append(train.currentStation.id)
# swapTrain.passengers += [[],[]]
# swapTrain.finished = False
# swapTrain.wasFinished = True
# swapTrain.nextStation =  train.currentStation
# swapTrain.enter =  train.currentStation.id
# swapTrain.potentialLine = line
# train.currentStation.enter.append(swapTrain)
# train.currentStation.scheduleTrainEnter()

# Push Routine
# pushTrain = pushStation.finishedTrains.pop()
# pushTrain.path.append(pushTrain.currentStation.id)
# pushTrain.path.append(alternativeStation.id)
# pushTrain.passengers += [[],[]]
# pushTrain.nextStation = alternativeStation
# pushTrain.finished = False
# pushTrain.wasFinished = True
# pushLine = getLineFromAToB(pushStation.id,alternativeStation.id)
# pushTrain.potentialLine = pushLine
# alternativeStation.enter.append(pushTrain)
# alternativeStation.potentialCapacity -= 1
# pushStation.depart.append(pushTrain)
# pushStation.potentialCapacity += 1

# Stop Routine
# curStation.potentialCapacity -= 1
# curTrain.nextStation.potentialCapacity += 1
# curStation.depart.remove(curTrain)
# curTrain.nextStation.enter.remove(curTrain)

# curTrain.nextStation = None
# curTrain.potentialLine.capacity += 1

# if curTrain.wasFinished:
#     curTrain.isFinished = True
#     curTrain.currentStation.finishedTrains.append(curTrain)
#     curTrain.wasFinished = False

# Drive Routine
# train.currentStation.depart.remove(train)
# train.nextStation.enter.remove(train)
# train.currentStation.capacity += 1
# train.nextStation.capacity -= 1

# train.line = train.potentialLine
# train.currentStation = None
# train.nextStation = None
# train.potentialLine = None

    def addStationToPath(self,station):
        self.path.append(self.currentStation.id)
        self.path.append(station.id)
        self.passengers += [[],[]]
        self.nextStation = station


    def enableFinishedTrain(self):
        self.isFinished = False
        self.wasFinished = True


    def disableFinishedTrain(self,station):
        self.isFinished = True
        self.wasFinished = False
        station.finishedTrains.append(self) # set finished Trains as function in station


    def swapWithTrain(self,train,line): # union with push
        self.currentStation.scheduleTrainDepart(self)
        self.addStationToPath(train.currentStation)
        self.enableFinishedTrain()
        train.currentStation.scheduleTrainEnter(self)
        self.potentialLine = line


    def pushTrainToStation(self,station,line): # union with swap
        self.currentStation.scheduleTrainDepart(self)
        self.addStationToPath(station)
        self.enableFinishedTrain()
        station.scheduleTrainEnter(self)
        self.potentialLine = line

    
    def setFinished(self):
        self.isFinished = True
        self.path = []
        self.passengers = []
        self.currentStation.finishedTrains.append(self) # set finished Trains as function in station


    def stop(self):
        self.currentStation.removeTrainFromDepartSchedule(self,True)
        self.nextStation.removeTrainFromEnterSchedule(self,True)
        self.nextStation = None
        self.potentialLine.removeTrain()
        self.potentialLine = None

        if self.wasFinished:
            self.disableFinishedTrain(self.currentStation)


    def drive(self):
        self.currentStation.removeTrainFromDepartSchedule(self,False)
        self.nextStation.removeTrainFromEnterSchedule(self,False)
        self.line = self.potentialLine
        print(self.nextStation.id," Before ",self.nextStation.capacity)
        self.nextStation.capacity -= 1
        print(self.nextStation.id," After ",self.nextStation.capacity,":",self.id)
        self.currentStation = None
        self.nextStation = None
        self.potentialLine = None