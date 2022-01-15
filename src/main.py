# region imports
from networkx.algorithms import swap
from networkx.algorithms.shortest_paths.generic import shortest_path_length
from networkx.algorithms.shortest_paths import shortest_path
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
from classes.line import Line
from itertools import repeat
from networkx import Graph
from operator import add
from sys import stdin
from numpy import inf
from math import ceil
# endregion

# region Variables
linesGraph = Graph()

wildcardTrains = []
placedTrains = []
passengers = []
stations = []
trains = []
lines = []
paths = []

currentTime = 0
simulationTime = 1
idletime = 3

passengersDict = {}
stationsDict = {}
linesDict = {}
trainsDict = {}
# endregion


# region In/Output
def loadInput():

    file = stdin.readlines()
    inputType = ""

    for i in file:
        inputType = getInputType(i, inputType)
        data = i.split(" ")

        if(len(data) < 2):
            continue

        if(data[0].find("#") != -1):
            continue
        if(data[0]== ""):
            continue
        if inputType == 0:
            station = Station(data[0], int(data[1].replace("\\n", "")))
            stations.append(station)
            stationsDict[station.id] = station

        elif inputType == 1:
            line = Line(
                        data[0],
                        data[1],
                        data[2],
                        float(data[3]), 
                        int(data[4].replace("\\n", "")))
            lines.append(line)
            linesDict[line.id] = line

        elif inputType == 2:
            curTrain = Train(
                            data[0], 
                            data[1], 
                            float(data[2]),
                            int(data[3].replace("\\n", "")),
                            idletime)
            trains.append(curTrain)

            if (curTrain.startingPosition == "*"):
                wildcardTrains.append(curTrain)

            else:
                placedTrains.append(curTrain)

        elif inputType == 3:
            passenger = Passengers(
                            data[0], 
                            data[1], 
                            data[2], 
                            int(data[3]),
                            int(data[4].replace("\\n", "")))
            passengers.append(passenger)
            passengersDict[passenger.id] = passenger


def getInputType(line, inputType):

    if line.find("[Stations]") != -1:
        return 0

    if line.find("[Lines]") != -1:
        return 1

    if line.find("[Trains]") != -1:
        return 2

    if line.find("[Passengers]") != -1:
        return 3

    return inputType





# Outputs final Result to Standard Output as defined in the Requirements
def writeOutput():

    outPutString = ""
    for train in trains:
        outPutString += train.write()

    for passenger in passengers:
        outPutString += passenger.write()

    print(outPutString)
# endregion


# region Lines graph
def buildLinesGraph():

    for x in stations:
        linesGraph.add_node(x.id)

    for line in lines:
        linesGraph.add_edge(
            line.stations[0],
            line.stations[1],
            weight=line.length,
            attr=line.id)
# endregion


# region Route calculation
# calculates shortes path for every passenger
# and saves [[path],groupSize,targetTime,id] in route
def calculateRoute():
    for passenger in passengers:
        paths.append([
                shortest_path(
                    linesGraph,
                    source=passenger.depatureStation,
                    target=passenger.destinationStation),
                passenger])


# sorts paths by length (longest paths first: optimization for patternMatching)
def sortpathsByLength():

    paths.sort(key=lambda x: (len(x[0]), -(x[1].targetTime*x[1].groupSize)),
               reverse=True)


# compares first path in paths with every other path
# of paths to find subpaths (paths that fit into first path)
def patternMatching():
    tempPaths = paths.copy()
    comparingPath = tempPaths[0]
    startStation = getStationById(comparingPath[0][0])
    endStation = getStationById(comparingPath[0][len(comparingPath[0]) - 1])

    currentTrainPassengers = [[] for i in repeat(None, len(comparingPath[0]))]
    currentTrainCapacity = [0] * len(comparingPath[0])
    currentTrainStops = [0] * len(comparingPath[0])

    possibleTrains, maxCapacity = getPossiblePlacedTrains(
        startStation
    )  # add trains which are currently at the start node
    # if no placed train is at the needed station (startNode)
    if isEmpty(possibleTrains) and not (isEmpty(wildcardTrains)):
        if startStation.capacity > 0:
            (possibleTrains,
             maxCapacity,
             ) = getPossibleWildcardTrains()  # add remaining wildcard trains
            startStation.placeTrain()

    # if no wildcard train remaining
    if isEmpty(possibleTrains):
        possibleTrain, maxCapacity = getNearestPossibleTrain(startStation)
        # add nearest train
        possibleTrains.append(possibleTrain)

    # sort possible trains by capacity
    possibleTrains.sort(key=lambda x: x.capacity)

    # if train is not full restart function on this train
    for path in tempPaths:
        i = 0
        currentPath = path[0]  # get station array from current path
        tempCapacity = [0] * len(comparingPath[0])

        for j in range(0, len(comparingPath[0])):
            if currentPath[i] == comparingPath[0][j]:
                i += 1

                if i < len(currentPath):
                    tempCapacity[j] += path[1].groupSize
                # add passenger groupSize to temp capacity array at pos j
            else:
                i = 0
                # reset temp capacity array
            if i == len(currentPath):
                # add passenger to train's passenger array

                potentialCapacity = list(map(add,currentTrainCapacity,tempCapacity))

                if max(potentialCapacity) > maxCapacity:
                    break

                paths.remove(path)

                currentTrainCapacity = potentialCapacity
                currentTrainPassengers[j - (len(currentPath) - 1)].append(path[1].id)
                currentTrainStops[j - (len(currentPath) - 1)] = 1
                currentTrainStops[j] = 1
                break
            elif (len(currentPath) - i) > (len(comparingPath[0]) - j):
                break

    chosenTrain = getBestTrainForCapacity(possibleTrains,
                                          max(currentTrainCapacity))
    addApproximateTimeNeeded(
                            chosenTrain,
                            currentTrainStops,
                            startStation,
                            endStation)
    chooseTrain(
        chosenTrain,
        currentTrainPassengers,
        comparingPath[0],
        startStation,
        endStation)


# endregion

# region Find possible trains
# gets all trains which are placed at the given station
def getPossiblePlacedTrains(station):

    possibleTrains = []
    maxCapacity = 0
    for train in placedTrains:
        if train.endStation is None:
            if train.currentStation.id == station.id:
                if maxCapacity < train.capacity:
                    maxCapacity = train.capacity

                possibleTrains.append(train)

        else:
            if train.endStation.id == station.id:
                if maxCapacity < train.capacity:
                    maxCapacity = train.capacity

                possibleTrains.append(train)

    return possibleTrains, maxCapacity


def getPossibleWildcardTrains():

    possibleTrains = []
    maxCapacity = 0
    for train in wildcardTrains:
        if maxCapacity < train.capacity:
            maxCapacity = train.capacity

        possibleTrains.append(train)

    return possibleTrains, maxCapacity


# gets nearest (considering: distance,speed,timeNeeded)
# train to the given station
def getNearestPossibleTrain(station):

    shortestTime = inf
    nearestTrain = None
    maxCapacity = 0
    for train in placedTrains:
        distance = shortest_path_length(
            linesGraph,
            source=train.currentStation.id,
            target=station.id,
            weight="weight",
        )
        time = train.timeNeeded + ceil(distance / train.speed)

        if time < shortestTime:
            shortestTime = time
            nearestTrain = train
            maxCapacity = train.capacity

    nearestTrain.timeNeeded += shortestTime
    return nearestTrain, maxCapacity
# endregion


# region Route assignment
# calculates the approximate time a train needs for a given route
def addApproximateTimeNeeded(train,
                             currentTrainStops,
                             startStation,
                             endStation):
    # get length of route
    length = shortest_path_length(linesGraph,
                                  source=startStation.id,
                                  target=endStation.id,
                                  weight="weight")
    stopCount = sum(currentTrainStops)
    train.timeNeeded += ceil(length / train.speed) + stopCount


# gets the train with the minimum capacity needed
# to carry a given number of passengers
# (train array needs to be sorted ascending by capacity)
def getBestTrainForCapacity(trains, capacity):
    index = 0
    for train in trains:
        # the first train which fits the capacity is returned
        if (train.capacity >= capacity):
            break
        index += 1
    trains = trains[index:]
    trains.sort(key=lambda x: x.speed)
    return trains[0]


# if chosen train is wildcard train place it
# on startStation and add it to placed trains
# + remove it from wildcard trains
def chooseWildcardTrain(train, startStation):

    if train in wildcardTrains:
        wildcardTrains.remove(train)
        train.startingPosition = startStation
        train.currentStation = startStation
        train.addAction(0, "Start", startStation.id)
        placedTrains.append(train)
        placedTrains.sort(key=lambda x: x.timeNeeded/x.speed)


def chooseTrain(train, passengers, path, startStation, endStation):

    chooseWildcardTrain(train, startStation)

    if train.endStation is None:
        if train.currentStation.id == path[0]:
            train.path += path
            train.passengers += passengers

        else:
            transitionStations = shortest_path(linesGraph,
                                               source=train.currentStation.id,
                                               target=startStation.id)
            train.path += transitionStations
            train.passengers += [[]] * len(transitionStations)
            train.path.pop()
            train.passengers.pop()
            train.path += path
            train.passengers += passengers

    elif train.endStation.id == path[0]:
        # remove last station from train's path and passengers,
        # because it is equal to the first in the new route and passengerArray
        train.path.pop()
        train.passengers.pop()
        train.path += path
        train.passengers += passengers

    else:
        transitionStations = shortest_path(
            linesGraph, source=train.endStation.id, target=startStation.id
        )
        train.path.pop()
        train.passengers.pop()
        train.path += transitionStations
        train.passengers += [[]] * len(transitionStations)
        # remove last station from train's path and passengers,
        # because it is equal to the first in the new route and passengerArray
        train.path.pop()
        train.passengers.pop()
        train.path += path
        train.passengers += passengers

    train.endStation = endStation
# endregion


# region Tick simulation
def addTrainToSchedule(train):
    # check if train is on line
    if train.line is None:
        # if train is not on line and has path
        if len(train.path) > 1:
            # get line
            line = getLineFromAToB(train.path[0],train.path[1])
            
            # check if line has capacity free
            if line.capacity > 0:
                # handle capacity
                train.nextStation = getStationById(train.path[1])
                train.currentStation.depart.append(train)
                train.currentStation.potentialCapacity += 1
                train.nextStation.enter.append(train)
                train.nextStation.potentialCapacity -= 1
                train.potentialLine = line
                line.capacity -= 1
    else:
        # if train is on line -> move train
        moveTrainOnLine(train)


def addFinishedTrainsToSchedule():
    for station in stations:
        if station.potentialCapacity < 0 and len(station.depart) == 0:
            for train in station.enter:
                if isEmpty(station.finishedTrains):
                    alternativeGraph = linesGraph.copy()
                    alternativeGraph.remove_edge(train.currentStation.id,station.id)
                    shortestPathTrainA = shortest_path(alternativeGraph, source=train.currentStation.id, target=train.nextStation.id)
                    alternativeLine = getLineFromAToB(shortestPathTrainA[0],shortestPathTrainA[1])
                    if not isEmpty(shortestPathTrainA) and alternativeLine.capacity > 0:
                        train.path.pop(0)
                        train.path = shortestPathTrainA[:-1] + train.path
                        train.passengers.pop(0)
                        train.passengers = [[] for i in repeat(None, len(shortestPathTrainA)-1)] + train.passengers
                        train.nextStation.removeTrainFromEnterSchedule(train,True)
                        train.nextStation = getStationById(train.path[1])
                        train.potentialLine.capacity += 1
                        train.potentialLine = alternativeLine
                        train.nextStation.scheduleTrainEnter(train)
                        alternativeLine.capacity -= 1
                    break
                else:
                    line = getLineFromAToB(train.currentStation.id,station.id)
                    if line.capacity > 0:
                        swapTrain = station.finishedTrains.pop()
                        swapTrain.swapWithTrain(train,line)
                        line.capacity -= 1

                    elif line.capacity == 0:
                        checkableStations = [station]
                        i=0
                        alternativeStation = None
                        while len(checkableStations) > i :
                            for lineTupel in linesGraph.edges(checkableStations[i].id):
                                if getStationById(checkableStations[i].id).previousStation == lineTupel[1]:
                                    continue
                                if len(getStationById(lineTupel[0]).finishedTrains) > 0:
                                    line = getLineFromAToB(lineTupel[0],lineTupel[1])
                                    if line.capacity > 0:
                                        lineStation = getStationById(lineTupel[1])
                                        lineStation.previousStation = lineTupel[0]
                                        if lineStation.potentialCapacity > 0:
                                            alternativeStation = lineStation
                                            break
                                        else:
                                            checkableStations.append(lineStation)
                                else:
                                    break
                            if alternativeStation!=None:
                                break
                            i+=1
                        if alternativeStation!=None:
                            previousStation = ""
                            pushStation = getStationById(alternativeStation.previousStation)
                            while previousStation != station.id:
                                pushLine = getLineFromAToB(pushStation.id,alternativeStation.id)
                                pushTrain = pushStation.finishedTrains.pop()
                                pushTrain.pushTrainToStation(alternativeStation,pushLine)
                                pushLine.capacity -= 1

                                previousStation = pushStation.id
                                alternativeStation = pushStation
                                
                                if alternativeStation.previousStation!="":
                                    pushStation = getStationById(alternativeStation.previousStation)


def removeTrainsFromSchedule():
    for station in stations:
        if station.potentialCapacity < 0:
            checkableTrains = []
            i = 0
            checkableTrains += station.enter
            while len(checkableTrains)>i:
                currentTrain = checkableTrains[i]
                currentStation = currentTrain.currentStation
                if currentStation.potentialCapacity > 0:
                    # stop train and fix capacities
                    currentTrain.stop()
                    if station.potentialCapacity >= 0:
                        break
                    else:
                        if len(checkableTrains)-1 == i and station.potentialCapacity < 0:
                            checkableTrains += station.enter
                        i+=1
                else:
                    # addNeigboursTochableStations
                    checkableTrains += currentStation.enter
                    i+=1


def moveTrains():
    for train in placedTrains:
        if train.line == None and not train.isFinished and train.nextStation != None:
            # assign train to line
            train.drive()
            train.addAction(simulationTime, "Depart", train.line.id)

            moveTrainOnLine(train)


def moveTrainOnLine(train):
    # increase train line progress
    train.progress += 1 / (train.line.length / train.speed)
    # enter station if station reached and station has space
    if (train.progress >= 1):
        # remove station from path
        train.path.pop(0)
        # assign station
        train.currentStation = getStationById(train.path[0])
        # handle station capacity
        # reset train line data
        train.progress = 0
        train.line.capacity += 1
        # remove old passengers
        train.passengers.pop(0)
        train.line = None


def scheduleTrainMovement():
    for train in placedTrains:
        # check if train has path
        if len(train.path) > 1:
            # check if train is in target station
            if (train.currentStation != None and train.currentStation.id == train.path[0]):
                # detrain passengers
                hasDetrainedPassengers = False
                newPassengers = []
                for passenger in train.boardedPassengers:
                    if train.currentStation.id == passenger.destinationStation:
                        passenger.addAction(simulationTime, "Detrain")
                        hasDetrainedPassengers = True

                    else:
                        newPassengers.append(passenger)

                train.boardedPassengers = newPassengers
                # check if train has passengers to board
                if len(train.passengers) > 0:
                    # check if train has passengers on this station to board
                    if len(train.passengers[0]) > 0:
                        # board passengers
                        for passenger in train.passengers[0]:
                            passengerObj = getPassengerById(passenger)
                            passengerObj.addAction(simulationTime,"Board",train.id)
                            train.boardedPassengers.append(passengerObj)

                        train.passengers[0] = []
                    elif not hasDetrainedPassengers:
                        # else move train to next station
                        addTrainToSchedule(train)

                else:
                    # else move train to next station
                    addTrainToSchedule(train)

            else:
                # else move forward train to target station
                addTrainToSchedule(train)

        else:
            # detrain passengers on final station of train
            newPassengers = []
            foundPassenger = False
            for passenger in train.boardedPassengers:
                if train.currentStation.id == passenger.destinationStation:
                    passenger.addAction(simulationTime, "Detrain")
                    foundPassenger = True
                else:
                    newPassengers.append(passenger)
            train.boardedPassengers = newPassengers

            if not foundPassenger and train.currentStation != None and not train.isFinished:
                train.setFinished()

    addFinishedTrainsToSchedule()
    removeTrainsFromSchedule()
    moveTrains()
# endregion


# region Utils
# gets id string as input
def getStationById(id):
    return stationsDict[id]


# gets id string as input
def getPassengerById(id):
    return passengersDict[id]


def getTrainById(id):
    return trains[id]


# gets id string as input
def getLineById(id):
    return linesDict[id]


def isEmpty(list):
    if len(list) == 0:
        return True
    else:
        return False


def getLineFromAToB(stationA,stationB):
    lineId = linesGraph.get_edge_data(stationA,stationB)["attr"]
    line = getLineById(lineId)
    return line


def initializeCurrentStations():
    for train in placedTrains:
        train.currentStation = getStationById(train.startingPosition)
        train.currentStation.placeTrain()


def initializeEmptyTrains():
    for train in placedTrains:
        if len(train.path)<=0:
            train.setFinished()


def printTrainPassengerAssignment():
    for train in trains:
        print(train.id, ": ", train.timeNeeded)
        pathString = ""

        for station in train.path:
            if station is not None:
                pathString += station + " "

        print(pathString)
        passengersString = ""

        for passengersStation in train.passengers:
            passengersString += "["

            for passenger in passengersStation:
                passengersString += passenger + " "

            passengersString += "]"

        print(passengersString)
# endregion


# region Main
if __name__ == "__main__":
    loadInput()
    buildLinesGraph()
    initializeCurrentStations()
    calculateRoute()
    sortpathsByLength()
    while len(paths) > 0:
        patternMatching()
    initializeEmptyTrains()

    passengersAvailable = True
    while passengersAvailable:
        scheduleTrainMovement()
        simulationTime += 1
        passengersAvailable = False

        for passenger in passengers:
            if not passenger.finished:
                passengersAvailable = True
                break
    writeOutput()
# endregion
