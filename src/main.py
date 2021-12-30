from numpy import inf
from classes.line import Line
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.shortest_paths import shortest_path
from networkx.algorithms.shortest_paths.generic import shortest_path_length
import math
import operator
from itertools import repeat
import sys

#region Variables
trains = []
placedTrains = []
wildcardTrains = []
stations = []
lines = []
passengers = []
paths = []
currentTime = 0
linesGraph = nx.Graph()
simulationTime = 0
#endregion

#region In/Output
def loadInput():
    file = sys.stdin.readlines()
    for i in file:
        data = i.split(" ")
        if data[0][0] == "S":
            stations.append(
                Station(data[0], int(data[1].replace("\\n", ""))))
        elif data[0][0] == "L":
            line = Line(data[0], float(data[3]),
                        int(data[4].replace("\\n", "")))
            for station in stations:
                if(station.id == data[1] or station.id == data[2]):
                    line.addStation(station)
            lines.append(line)
        elif (data[0][0] == "T"):
            curTrain = Train(data[0], data[1], float(
                data[2]), int(data[3].replace("\\n", "")))
            trains.append(curTrain)
            if (curTrain.startingPosition == "*"):
                wildcardTrains.append(curTrain)
            else:
                placedTrains.append(curTrain)
        elif data[0][0] == "P":
            passenger = Passengers(data[0], int(
                data[3]), int(data[4].replace("\\n", "")))
            for station in stations:
                if station.id == data[1]:
                    passenger.depatureStation = station
                elif station.id == data[2]:
                    passenger.destinationStation = station
            passengers.append(passenger)

#Old Textfile based version
# def loadInput():
#     with open('input.txt') as f:
#         file = f.readlines()
#         for i in file:
#             data = i.split(" ")
#             if data[0][0] == "S":
#                 stations.append(
#                     Station(data[0], int(data[1].replace("\\n", ""))))
#             elif data[0][0] == "L":
#                 line = Line(data[0], float(data[3]),
#                             int(data[4].replace("\\n", "")))
#                 for station in stations:
#                     if(station.id == data[1] or station.id == data[2]):
#                         line.addStation(station)
#                 lines.append(line)
#             elif (data[0][0] == "T"):
#                 curTrain = Train(data[0], data[1], float(
#                     data[2]), int(data[3].replace("\\n", "")))
#                 trains.append(curTrain)
#                 if (curTrain.startingPosition == "*"):
#                     wildcardTrains.append(curTrain)
#                 else:
#                     placedTrains.append(curTrain)
#             elif data[0][0] == "P":
#                 passenger = Passengers(data[0], int(
#                     data[3]), int(data[4].replace("\\n", "")))
#                 for station in stations:
#                     if station.id == data[1]:
#                         passenger.depatureStation = station
#                     elif station.id == data[2]:
#                         passenger.destinationStation = station
#                 passengers.append(passenger)

#Outputs final Result to Standard Output as defined in the Requirements
def writeOutput():
    outPutString = ""
    for train in trains:
        outPutString += train.write()
    for passenger in passengers:
        outPutString += passenger.write()

    print(outPutString)

#Old Version for File-based Output
#def writeOutput():
#    file = open("output.txt", "w")
#    file.close()
#    for train in trains:
#        train.write()
#    for passenger in passengers:
#        passenger.write()
#endregion

#region Lines graph
def buildLinesGraph():
    for x in stations:
        linesGraph.add_node(x.id)
    for line in lines:
        linesGraph.add_edge(
            line.stations[0].id, line.stations[1].id, weight=line.length, attr=line.id)


def drawLinesGraph():
    # Debug output um Graph zu zeichnen
    nx.draw(linesGraph, with_labels=True)
    plt.show()
#endregion

#region Route generator
#region Route calculation
#calculates shortes path for every passenger and saves [[path],groupSize,targetTime,id] in route
def calculateRoute():
    for passenger in passengers:
        paths.append([shortest_path(linesGraph, source=passenger.depatureStation.id,target=passenger.destinationStation.id),
                	    passenger])

#sorts paths by length (longest paths first: optimization for patternMatching)
def sortpathsByLength():
    paths.sort(key=lambda x: (len(x[0]), -x[1].targetTime), reverse=True)

#compares first path in paths with every other path of paths to find subpaths (paths that fit into first path)
def patternMatching():
    comparingPath = paths[0]
    startStation = getStationById(comparingPath[0][0])
    endStation = getStationById(comparingPath[0][len(comparingPath[0])-1])
    tempPaths = paths.copy()

    currentTrainPassengers = [[] for i in repeat(None, len(comparingPath[0]))]
    currentTrainCapacity = [0] * len(comparingPath[0])
    currentTrainStops = [0] * len(comparingPath[0])

    possibleTrains,maxCapacity = getPossiblePlacedTrains(startStation) #add trains which are currently at the start node
    #if no placed train is at the needed station (startNode)
    if(isEmpty(possibleTrains) and not(isEmpty(wildcardTrains))):
        possibleTrains,maxCapacity = getPossibleWildcardTrains() #add remaining wildcard trains
    #if no wildcard train remaining
    if(isEmpty(possibleTrains)):
        possibleTrain,maxCapacity = getNearestPossibleTrain(startStation)
        possibleTrains.append(possibleTrain) #add nearest train
    possibleTrains.sort(key=lambda x: x.capacity) #sort possible trains by capacity
    
    #potential functions for main loop
    # - getApproximateTime
    # - capacityCheck
    # - generateFinalRoute
    # - modifyTrainRoute
    # - buildPassengerArray
    # - clearAssignedpaths
    # if train is not full restart function on this train
    for path in tempPaths:
        i=0
        currentPath = path[0] #get station array from current path
        tempCapacity = [0] * len(comparingPath[0])
        for j in range(0, len(comparingPath[0])):
            if(currentPath[i]==comparingPath[0][j]):
                i += 1
                if(i<len(currentPath)):
                    tempCapacity[j]+=path[1].groupSize
                #add passenger groupSize to temp capacity array at pos j
            else:
                i = 0
                #reset temp capacity array
            if (i == len(currentPath)):
                #add passenger to train's passenger array

                potentialCapacity = list(map(operator.add, currentTrainCapacity, tempCapacity))
                if(max(potentialCapacity)>maxCapacity):
                    break

                paths.remove(path)

                currentTrainCapacity = potentialCapacity
                currentTrainPassengers[j-(len(currentPath)-1)].append(path[1].id)
                currentTrainStops[j-(len(currentPath)-1)] = 1
                currentTrainStops[j] = 1
                break
            elif(len(currentPath)-i>len(comparingPath)-j):
                break
    
    chosenTrain = getBestTrainForCapacity(possibleTrains, max(currentTrainCapacity))
    addApproximateTimeNeeded(chosenTrain, currentTrainStops, startStation, endStation)
    chooseTrain(chosenTrain,currentTrainPassengers,comparingPath[0],startStation,endStation)
#endregion

#region Find possible trains
#gets all trains which are placed at the given station
def getPossiblePlacedTrains(station):
    possibleTrains = []
    maxCapacity = 0
    for train in placedTrains:
        if(train.endStation == None):
            if(train.currentStation.id == station.id):
                if(maxCapacity < train.capacity):
                    maxCapacity = train.capacity
                possibleTrains.append(train)
        else:
            if(train.endStation.id == station.id):
                if(maxCapacity < train.capacity):
                    maxCapacity = train.capacity
                possibleTrains.append(train)
    return possibleTrains, maxCapacity

def getPossibleWildcardTrains():
    possibleTrains = []
    maxCapacity = 0
    for train in wildcardTrains:
        if (maxCapacity < train.capacity):
            maxCapacity = train.capacity
        possibleTrains.append(train)
    return possibleTrains, maxCapacity

#gets nearest (considering: distance,speed,timeNeeded) train to the given station
def getNearestPossibleTrain(station):
    shortestTime = inf
    nearestTrain = None
    maxCapacity = 0
    for train in placedTrains:
        distance = shortest_path_length(linesGraph, source=train.currentStation.id, target=station.id, weight="weight")
        time = train.timeNeeded+math.ceil(distance/train.speed)
        if(time < shortestTime):
            shortestTime = time
            nearestTrain = train
            maxCapacity = train.capacity
    nearestTrain.timeNeeded+=shortestTime
    return nearestTrain, maxCapacity
#endregion

#region Route assignment
#calculates the approximate time a train needs for a given route
def addApproximateTimeNeeded(train, currentTrainStops, startStation, endStation):
    length = shortest_path_length(linesGraph, source=startStation.id, target=endStation.id, weight="weight") #get length of route
    stopCount = sum(currentTrainStops)
    train.timeNeeded += math.ceil(length / train.speed) + stopCount

#gets the train with the minimum capacity needed to carry a given number of passengers
#(train array needs to be sorted ascending by capacity)
def getBestTrainForCapacity(trains, capacity):
    for train in trains:
        if(train.capacity >= capacity): #the first train which fits the capacity is returned
            return train

#if chosen train is wildcard train place it on startStation and add it to placed trains
# + remove it from wildcard trains
def chooseWildcardTrain(train,startStation):
    if(train in wildcardTrains):
        wildcardTrains.remove(train)
        train.startingPosition = startStation
        train.currentStation = startStation
        placedTrains.append(train)
        placedTrains.sort(key=lambda x: x.timeNeeded)


def chooseTrain(train,passengers,path,startStation,endStation):

    chooseWildcardTrain(train,startStation)

    if (train.endStation==None):
        if (train.currentStation.id==path[0]):
            train.path += path
            train.passengers += passengers
        else:
            transitionStations = shortest_path(linesGraph, source=train.currentStation.id, target=startStation.id)
            train.path += transitionStations
            train.passengers += [[]] * len(transitionStations)
            train.path.pop()
            train.passengers.pop()
            train.path += path
            train.passengers += passengers
    elif (train.endStation.id==path[0]):
        #remove last station from train's path and passengers, because it is equal to the first in the new route and passengerArray
        train.path.pop()
        train.passengers.pop()
        train.path += path
        train.passengers += passengers
    else:
        transitionStations = shortest_path(linesGraph, source=train.currentStation.id, target=startStation.id)
        train.path += transitionStations
        train.passengers += [[]] * len(transitionStations)
        #remove last station from train's path and passengers, because it is equal to the first in the new route and passengerArray
        train.path.pop()
        train.passengers.pop()
        train.path += path
        train.passengers += passengers

    train.endStation=endStation
#endregion
#endregion

#region Tick simulation
def moveTrain(train):
    #check if train is on line
    if(train.line == None):
        #if train is not on line and has path
        if(len(train.path) > 1):
            #get line
            lineId = linesGraph.get_edge_data(
                train.path[0], train.path[1])["attr"]
            line = getLineById(lineId)
            #check if line has capacity free
            if(line.capacity > 0):
                #handle capacity
                line.capacity -= 1
                train.currentStation.capacity += 1
                #assign train to line
                train.currentStation = None
                train.line = line
                train.addAction(simulationTime,
                                "Depart", train.line.id)
                moveTrainOnLine(train)
    else:
        #if train is on line -> move train
        moveTrainOnLine(train)


def moveTrainOnLine(train):
    #increase train line progress
    train.progress += 1/(train.line.length/train.speed)
    #enter station if station reached and station has space
    if(train.progress >= 1 and getLineById(train.path[0]).capacity > 0):
        #remove station from path
        train.path.pop(0)
        #assign station
        train.currentStation = getStationById(train.path[0])
        #handle station capacity
        train.currentStation.capacity -= 1
        #reset train line data
        train.progress = 0
        train.line.capacity += 1
        #remove old passengers
        train.passengers.pop(0)
        train.line = None


def moveTrains():
    for train in trains:
        #check if train has path
        if(len(train.path) > 1):
            #check if train is in target station
            if(train.currentStation != None and train.currentStation.id == train.path[0]):
                #detrain passengers
                hasDetrainedPassengers = False
                newPassengers = []
                for passenger in train.boardedPassengers:
                    if(train.currentStation == passenger.destinationStation):
                        passenger.addAction(
                            simulationTime, "Detrain")
                        hasDetrainedPassengers = True
                    else:
                        newPassengers.append(passenger)
                train.boardedPassengers = newPassengers
                #check if train has passengers to board
                if(len(train.passengers) > 0):
                    #check if train has passengers on this station to board
                    if(len(train.passengers[0]) > 0):
                        #board passengers
                        for passenger in train.passengers[0]:
                            passengerObj = getPassengerById(passenger)
                            passengerObj.addAction(
                                simulationTime, "Board", train.id)
                            train.boardedPassengers.append(passengerObj)
                        train.passengers[0] = []
                    elif(not hasDetrainedPassengers):
                        #else move train to next station
                        moveTrain(train)
                else:
                    #else move train to next station
                    moveTrain(train)
            else:
                #else move forward train to target station
                moveTrain(train)
        else:
            #detrain passengers on final station of train
            newPassengers = []
            for passenger in train.boardedPassengers:
                if(train.currentStation == passenger.destinationStation):
                    passenger.addAction(simulationTime, "Detrain")
                else:
                    newPassengers.append(passenger)
            train.boardedPassengers = newPassengers
#endregion

#region Utils
#gets id string as input
def getStationById(id):
    return stations[int(id[1:])-1]

#gets id string as input
def getPassengerById(id):
    return passengers[int(id[1:])-1]

#gets id string as input
def getLineById(id):
    return lines[int(id[1:])-1]


def isEmpty(list):
    if(len(list) == 0):
        return True
    else:
        return False

def getOverallDelay():
    delay = 0
    for passenger in passengers:
        if(passenger.delay > 0):
            delay += passenger.delay
    #print("Gesamtverspätung: ", delay)

def initializeCurrentStations():
    for train in placedTrains:
        train.currentStation=getStationById(train.startingPosition)

def printTrainPassengerAssignment():
    for train in trains:
        #print(train.id,": ",train.timeNeeded)
        pathString=""
        for station in train.path:
            if(station!=None):
                pathString+=station+" "
        #print(pathString)
        passengersString=""
        for passengersStation in train.passengers:
            passengersString+="["
            for passenger in passengersStation:
                passengersString+=passenger+" "
            passengersString+="]"
        #print(passengersString)
#endregion

#region Main
if __name__ == "__main__":
    loadInput()
    buildLinesGraph()
    # drawLinesGraph()
    initializeCurrentStations()
    calculateRoute()
    sortpathsByLength()
    
    while(len(paths)>0):
        patternMatching()
        # print(len(paths))

    #printTrainPassengerAssignment()

    passengersAvailable = True
    while (passengersAvailable):
        moveTrains()
        simulationTime+=1
        passengersAvailable = False
        for passenger in passengers:
            if(not passenger.finished):
                # print(passenger.id)
                passengersAvailable = True
                break

    writeOutput()
    # getOverallDelay()
#endregion