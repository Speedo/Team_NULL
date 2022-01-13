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
import os
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

currentStation = None
# endregion


# region In/Output
# if(os.environ.get("USERNAME") != "speedo"):
# def loadInput():
#     with open('input.txt') as f:

#         file = f.readlines()
#         inputType = ""

#         for i in file:
#             inputType = getInputType(i, inputType)
#             data = i.split(" ")

#             if(len(data) < 2):
#                 continue
            
#             if(data[0].find("#") != -1):
#                 continue
#             if(data[0]== ""):
#                 continue
#             if inputType == 0:
#                 station = Station(data[0], int(data[1].replace("\\n", "")))
#                 stations.append(station)
#                 stationsDict[station.id] = station

#             elif inputType == 1:
#                 line = Line(
#                             data[0],
#                             data[1],
#                             data[2],
#                             float(data[3]), 
#                             int(data[4].replace("\\n", "")))
#                 lines.append(line)
#                 linesDict[line.id] = line

#             elif inputType == 2:
#                 curTrain = Train(
#                                 data[0], 
#                                 data[1], 
#                                 float(data[2]),
#                                 int(data[3].replace("\\n", "")),
#                                 idletime)
#                 trains.append(curTrain)
#                 trainsDict[curTrain.id] = curTrain

#                 if (curTrain.startingPosition == "*"):
#                     wildcardTrains.append(curTrain)

#                 else:
#                     placedTrains.append(curTrain)

#             elif inputType == 3:
#                 passenger = Passengers(
#                                 data[0], 
#                                 data[1], 
#                                 data[2], 
#                                 int(data[3]),
#                                 int(data[4].replace("\\n", "")))
#                 passengers.append(passenger)
#                 passengersDict[passenger.id] = passenger

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
def moveTrain(train):
    # check if train is on line
    if train.line is None:
        # if train is not on line and has path
        if len(train.path) > 1:
            # get line
            lineId = linesGraph.get_edge_data(
                                    train.path[0],
                                    train.path[1])["attr"]
            line = getLineById(lineId)
            
            train.nextStation = getStationById(train.path[1])
            # check if line has capacity free
            if line.capacity > 0:
                # handle capacity
                train.currentStation.depart.append(train)
                train.currentStation.potentialCapacity += 1
                train.nextStation.enter.append(train)
                train.nextStation.potentialCapacity -= 1
                train.enter = train.path[1]
                train.potentialLine = line
                line.capacity -= 1
                
                # train.currentStation.capacity += 1
                # targetStation.capacity -= 1
                # # assign train to line
                # train.currentStation = None
                # train.line = line
                # train.addAction(simulationTime, "Depart", train.line.id)
                # moveTrainOnLine(train)
    else:
        # if train is on line -> move train
        moveTrainOnLine(train)

# def moveTrain(train):
#     # check if train is on line
#     if train.line is None:
#         # if train is not on line and has path
#         if len(train.path) > 1:
#             # get line
#             lineId = linesGraph.get_edge_data(
#                                     train.path[0],
#                                     train.path[1])["attr"]
#             line = getLineById(lineId)
#             targetStation = getStationById(train.path[1])

#             # check if line has capacity free
#             if line.capacity > 0 and targetStation.capacity > 0:
#                 # handle capacity
#                 line.capacity -= 1
#                 train.currentStation.capacity += 1
#                 targetStation.capacity -= 1
#                 # assign train to line
#                 train.currentStation = None
#                 train.line = line
#                 train.addAction(simulationTime, "Depart", train.line.id)
#                 moveTrainOnLine(train)
#     else:
#         # if train is on line -> move train
#         moveTrainOnLine(train)


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


def moveTrains():
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
                            passengerObj.addAction(simulationTime,
                                                   "Board",
                                                   train.id)
                            train.boardedPassengers.append(passengerObj)

                        train.passengers[0] = []
                    elif not hasDetrainedPassengers:
                        # else move train to next station
                        moveTrain(train)

                else:
                    # else move train to next station
                    moveTrain(train)

            else:
                # else move forward train to target station
                moveTrain(train)

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
            if(not foundPassenger):
                train.finished = True
                train.currentStation.finishedTrains.append(train)

    

    for station in stations:
        if station.potentialCapacity < 0 and len(station.depart) == 0:
            for train in station.enter:
                if len(station.finishedTrains) <= 0:
                    break
                else:
                    lineId = linesGraph.get_edge_data(
                        train.currentStation.id,
                        station.id)["attr"]
                    line = getLineById(lineId)
                    if line.capacity > 0:
                        swapTrain = station.finishedTrains.pop()
                        swapTrain.currentStation.depart.append(swapTrain)
                        swapTrain.currentStation.potentialCapacity += 1
                        train.currentStation.enter.append(swapTrain)
                        train.currentStation.potentialCapacity -= 1
                        swapTrain.path.append(station.id)
                        swapTrain.path.append(train.currentStation.id)
                        swapTrain.passengers += [[],[]]
                        swapTrain.finished = False
                        swapTrain.nextStation =  train.currentStation
                        swapTrain.enter =  train.currentStation.id
                        swapTrain.potentialLine = line
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
                                    lineId = linesGraph.get_edge_data(
                                        lineTupel[0],
                                        lineTupel[1])["attr"]
                                    line = getLineById(lineId)
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
                                pushTrain = pushStation.finishedTrains.pop()
                                pushTrain.path.append(pushStation.id)
                                pushTrain.path.append(alternativeStation.id)
                                pushTrain.nextStation = alternativeStation
                                pushTrain.enter = alternativeStation.id
                                pushTrain.potentialLine = getLineById(linesGraph.get_edge_data(pushStation.id,alternativeStation.id)["attr"])
                                pushTrain.passengers += [[],[]]
                                pushTrain.finished = False
                                alternativeStation.enter.append(pushTrain)
                                alternativeStation.potentialCapacity -= 1
                                pushStation.depart.append(pushTrain)
                                pushStation.potentialCapacity += 1
                                previousStation = pushStation.id
                                alternativeStation = pushStation
                                if alternativeStation.previousStation!="":
                                    pushStation = getStationById(alternativeStation.previousStation)

    print("--- ",simulationTime," ---")
    print("Before")
    for station in stations:
        print(station.id,":",station.potentialCapacity)

    for station in stations:
        if station.potentialCapacity < 0:
            checkableTrains = []
            i = 0
            checkableTrains += station.enter
            while len(checkableTrains)>i:
                curTrain = checkableTrains[i]
                curStation = curTrain.currentStation
                if curStation.potentialCapacity > 0:
                    # stop train and fix capacities
                    enterStation = getStationById(curTrain.enter)
                    curStation.potentialCapacity -= 1
                    enterStation.potentialCapacity += 1
                    curStation.depart.remove(curTrain)
                    enterStation.enter.remove(curTrain)
                    curTrain.enter = ""
                    
                    if station.potentialCapacity >= 0:
                        break
                    else:
                        i+=1
                else:
                    # addNeigboursTochableStations
                    checkableTrains += curStation.enter
                    i+=1
    
    print("--- ",simulationTime," ---")
    print("After")
    for station in stations:
        print(station.id,":",station.potentialCapacity)

    # print("Simulation Step: ",simulationTime)
    # for station in stations:
    #     entered = ""
    #     departed = ""
    #     for train in station.enter:
    #         entered += train.id + ", "
    #     for train in station.depart:
    #         departed += train.id + ", "
    #     if entered == "":
    #         entered = "--"
    #     if departed == "":
    #         departed = "--"
    #     print(station.id,": ",entered,"; ",departed,"; ",station.potentialCapacity)

    print("Trains")
    for train in placedTrains:
        if train.line is None and not train.finished:
            # if train is not on line and has path
            if (train.enter==""):
                print(train.id,":",train.currentStation.depart)
            if train.enter != "":
                # train.currentStation.capacity += 1
                # getStationById(train.path[1]).capacity -= 1
                # assign train to line
                train.currentStation.depart.remove(train)
                train.nextStation.enter.remove(train)
                print("StationCheck ",train.id,":", train.currentStation.id,"::",train.nextStation.id)
                train.currentStation.capacity += 1
                train.nextStation.capacity -= 1
                train.line = train.potentialLine
                train.enter = ""
                train.currentStation = None
                train.potentialLine = None
                train.addAction(simulationTime, "Depart", train.line.id)

                moveTrainOnLine(train)

# endregion

def traceTrainRoute(train):
    if train.currentStation.id==currentStation:
        train.isNeeded = True
    else:
        for trainRecursive in getStationById(train.enter).depart:
            return traceTrainRoute(trainRecursive) 

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

def initializeCurrentStations():
    for train in placedTrains:
        train.currentStation = getStationById(train.startingPosition)
        train.currentStation.placeTrain()


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

    printTrainPassengerAssignment()

    for train in placedTrains:
        if len(train.path)<=0:
            train.finished=True
            train.currentStation.finishedTrains.append(train)

    # moveTrains()
    # print("--- All Trains ---")
    # for train in placedTrains:
    #     if(train.currentStation!=None):
    #         print(train.id,": ",train.currentStation.id)
    #     else:
    #         print(train.id,": ",train.line.id)
    # simulationTime += 1

    passengersAvailable = True
    while passengersAvailable:
        moveTrains()
        simulationTime += 1
        passengersAvailable = False
        
        print("--- ",simulationTime," ---")
        print("Capacity")
        for station in stations:
            print(station.id,":",station.capacity)
        for passenger in passengers:
            if not passenger.finished:
                passengersAvailable = True
                break
    writeOutput()
# endregion
