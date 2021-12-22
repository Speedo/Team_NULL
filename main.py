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

#region Variables
trains = []
placedTrains = []
wildcardTrains = []
stations = []
lines = []
passengers = []
routes = []
currentTime = 0
linesGraph = nx.Graph()
simulationTime = 0
#endregion

#region In/Output
def loadInput():
    with open('input.txt') as f:
        file = f.readlines()
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

def writeOutput():
    file = open("output.txt", "w")
    file.close()
    for train in trains:
        train.write()
    for passenger in passengers:
        passenger.write()
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
        routes.append([shortest_path(linesGraph, source=passenger.depatureStation.id,
                      target=passenger.destinationStation.id), passenger.groupSize, passenger.targetTime, passenger.id])

#sorts routes by length (longest paths first: optimization for patternMatching)
def sortRoutesByLength():
    routes.sort(key=lambda x: (len(x[0]), -x[2]), reverse=True)

#compares first path in routes with every other path of routes to find subroutes (paths that fit into first path)
def patternMatching():
    comparingRoute = routes[0][0]
    matchingRoutes = []
    matchingRoutes.append(routes[0])
    for i in range(1, len(routes)):
        ix = 0
        currentRoute = routes[i][0]
        for j in range(0, len(comparingRoute)):
            if (comparingRoute[j] == currentRoute[ix]):
                ix += 1
                j += 1
            else:
                ix = 0
                j += 1
            if (ix == len(currentRoute)):
                matchingRoutes.append(routes[i])
                break
            elif(len(currentRoute)-ix>len(comparingRoute)-j):
                break
    return matchingRoutes
#endregion

#region Find possible trains
#gets all trains which are placed at the given station
def getPossiblePlacedTrains(station):
    placedTrains.sort(key=lambda x: x.timeNeeded)
    possibleTrains = []
    for train in placedTrains:
        if(train.endStation == None):
            if(train.currentStation.id == station.id):
                possibleTrains.append(train)
        else:
            if(train.endStation.id == station.id):
                possibleTrains.append(train)
    return possibleTrains

#gets nearest (considering: distance,speed,timeNeeded) train to the given station
def getNearestPossibleTrain(station):
    shortestTime = inf
    nearestTrain = None
    placedTrains.sort(key=lambda x: x.timeNeeded)
    for train in placedTrains:
        distance = shortest_path_length(linesGraph, source=train.currentStation.id, target=station.id, weight="weight")
        time = train.timeNeeded+math.ceil(distance/train.speed)
        if(time < shortestTime):
            shortestTime = time
            nearestTrain = train
    return nearestTrain


def getPossibleTrainsForRoute(startNode):
    possibleTrains = getPossiblePlacedTrains(startNode) #add trains which are currently at the start node
    #if no placed train is at the needed station (startNode)
    if(isEmpty(possibleTrains)):
        possibleTrains = wildcardTrains #add remaining wildcard trains
    #if no wildcard train remaining
    if(isEmpty(possibleTrains)):
        possibleTrains.append(getNearestPossibleTrain(startNode)) #add nearest train
    possibleTrains.sort(key=lambda x: x.capacity) #sort possible trains by capacity
    return possibleTrains
#endregion

#region Route assignment
#calculates the approximate time a train needs for a given route
def calculateApproximateTimeNeeded(train, routes, startStation, endStation):
    length = shortest_path_length(linesGraph, source=startStation.id, target=endStation.id, weight="weight") #get length of route
    finalStations = []
    for route in routes:
        finalStations.append(route[0][0]) #add boarding station
        finalStations.append(route[0][len(route[0])-1]) #add detraining station
    stopCount = len(set(finalStations)) #get amount of stops where passengers board or detrain
    return math.ceil(length / train.speed) + stopCount

#generates a final route and which passengers to carry based on the available train capacity
def generateFinalRoute(matchingRoutes, currentCapacity, maxCapacity):
    finalRoute = []
    for route in matchingRoutes:
        #if train has enough capacity for the passengers
        if((currentCapacity+route[1]) <= maxCapacity):
            finalRoute.append(route) #add them to finalRoute
            currentCapacity+=route[1] #increase current capacity by passenger groupSize
    return finalRoute

#gets the train with the minimum capacity needed to carry a given number of passengers
#(train array needs to be sorted ascending by capacity)
def getBestTrainForCapacity(trains, capacity):
    for train in trains:
        if(train.capacity >= capacity): #the first train which fits the capacity is returned
            return train

#adds given route and passengers to a train
def modifyTrainRoute(train,route,passengers):
    for station in route:
        train.path.append(getStationById(station)) #add stations of route
    train.passengers+=(passengers) #add passengers

#if chosen train is wildcard train place it on startStation and add it to placed trains
# + remove it from wildcard trains
def chooseWildcardTrain(train,startStation):
    if(train in wildcardTrains):
        wildcardTrains.remove(train)
        train.startingPosition = startStation
        train.currentStation = startStation
        placedTrains.append(train)

#
def addTransitionRoute(train,startStation,endStation):
    transitionStations = shortest_path(linesGraph, source=startStation.id, target=endStation)
    train.timeNeeded+=calculateApproximateTimeNeeded(train,[],startStation,getStationById(endStation))
    if(not isEmpty(train.path)):
        train.path.pop()
        train.passengers.pop()
    for station in transitionStations:
        train.path.append(getStationById(station))
        train.passengers.append("")

def chooseTrain(train,timeNeeded,startStation,endStation,finalRoute):
    passengerArray=buildPassengerArray(finalRoute)
    mainRoute=finalRoute[0][0]

    chooseWildcardTrain(train,startStation)
    
    if (train.endStation==None):
        if (train.currentStation.id==mainRoute[0]):
            modifyTrainRoute(train,mainRoute,passengerArray)
        else:
            addTransitionRoute(train,train.currentStation,mainRoute[0])
            #remove last station from train's path and passengers, because it is equal to the first in the new route and passengerArray
            train.path.pop()
            train.passengers.pop()
            modifyTrainRoute(train,mainRoute,passengerArray)
    elif (train.endStation.id==mainRoute[0]):
        #remove last station from train's path and passengers, because it is equal to the first in the new route and passengerArray
        train.path.pop()
        train.passengers.pop()
        modifyTrainRoute(train,mainRoute,passengerArray)
    else:
        addTransitionRoute(train,train.endStation,mainRoute[0])
        #remove last station from train's path and passengers, because it is equal to the first in the new route and passengerArray
        train.path.pop()
        train.passengers.pop()
        modifyTrainRoute(train,mainRoute,passengerArray)

    train.timeNeeded+=timeNeeded
    train.endStation=endStation

def buildPassengerArray(finalRoute):
    passengers = []
    for i in range(0, len(finalRoute[0][0])):
        stationPassengers = []
        for route in finalRoute:
            if finalRoute[0][0][i] == route[0][0]:
                stationPassengers.append(getPassengerById(route[3]))
        passengers.append(stationPassengers)
    return passengers

def clearAssignedRoutes(finalRoute):
    for route in finalRoute:
        #if route in routes
        if(route in routes):
            #remove route from routes (passenger is already assigned)
            routes.remove(route)
#endregion

def routeGeneration():
    finalRoute = []
    chosenTrain = None
    currentCapacity = 0

    #get route and matching subroutes
    matchingRoutes=patternMatching()
    
    #get start-/endstation
    startStation=getStationById(matchingRoutes[0][0][0])
    endStation=getStationById(matchingRoutes[0][0][len(matchingRoutes[0][0])-1])

    # get trains nearby or at startStation
    possibleTrains = getPossibleTrainsForRoute(startStation)

    # add father route (longest route) to final route
    finalRoute.append(matchingRoutes[0])

    # add passengers from father route to capacity count
    currentCapacity += matchingRoutes[0][1]
    # remove father route from matchingRoutes
    matchingRoutes.remove(matchingRoutes[0])
    # sort matchingRoutes by group size
    matchingRoutes.sort(key=lambda x: x[2]*x[1])
    #get train with most capacity (possibleTrains are sorted by capacity)
    maxCapacity=possibleTrains[len(possibleTrains)-1].capacity
    #add matchingRoutes to finalRoutes based on available capacity
    finalRoute+=generateFinalRoute(matchingRoutes,currentCapacity,maxCapacity)
    #get best train for needed route capacity
    chosenTrain=getBestTrainForCapacity(possibleTrains,currentCapacity)
    
    #calculate time train needs for the route (approximately)
    timeNeeded=calculateApproximateTimeNeeded(chosenTrain,finalRoute,startStation,endStation)
    
    #set all variables in chosenTrain
    chooseTrain(chosenTrain,timeNeeded,startStation,endStation,finalRoute)

    #delete assigned passengers from routes
    clearAssignedRoutes(finalRoute)
#endregion

#region Tick simulation
def moveTrain(train):
    #check if train is on line
    if(train.line == None):
        #if train is not on line and has path
        if(len(train.path) > 1):
            #get line
            lineId = linesGraph.get_edge_data(
                train.path[0].id, train.path[1].id)["attr"]
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
    if(train.progress >= 1 and train.path[0].capacity > 0):
        #remove station from path
        train.path.pop(0)
        #assign station
        train.currentStation = train.path[0]
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
            if(train.currentStation == train.path[0]):
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
                            passenger.addAction(
                                simulationTime, "Board", train.id)
                            train.boardedPassengers.append(passenger)
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
def getStationById(id):
    for i in range(0, len(stations)):
        if(stations[i].id == id):
            return stations[i]


def getPassengerById(id):
    for i in range(0, len(passengers)):
        if(passengers[i].id == id):
            return passengers[i]


def getLineById(id):
    for line in lines:
        if (line.id == id):
            return line


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
    print("Gesamtverspätung: ", delay)

def initializeCurrentStations():
    for train in trains:
        train.currentStation=getStationById(train.startingPosition)

def printTrainPassengerAssignment():
    for train in trains:
        print(train.id,": ",train.timeNeeded)
        pathString=""
        for station in train.path:
            if(station!=None):
                pathString+=station.id+" "
        print(pathString)
        passengersString=""
        for passengersStation in train.passengers:
            passengersString+="["
            for passenger in passengersStation:
                passengersString+=passenger.id+" "
            passengersString+="]"
        print(passengersString)
#endregion

#region Main
if __name__ == "__main__":
    loadInput()
    buildLinesGraph()
    # drawLinesGraph()
    initializeCurrentStations()
    calculateRoute()
    sortRoutesByLength()
    
    while(len(routes)>0):
        routeGeneration()

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
    getOverallDelay()
#endregion