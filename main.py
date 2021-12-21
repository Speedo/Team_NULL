from networkx.generators.expanders import paley_graph
from numpy import Inf, inf
from classes.line import Line
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
from classes.simulationTime import SimulationTime
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.shortest_paths import shortest_path, weighted
from networkx.algorithms.shortest_paths.generic import shortest_path_length
import math

#region Variables
trains = []
placed_trains = []
wildcard_trains = []
stations = []
lines = []
passengers = []
routes = []
currentTime = 0
lines_graph = nx.Graph()
simulationTime = SimulationTime()
simulationTime.currentTick = 0
#endregion

#region In/Output
def load_input():
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
                    wildcard_trains.append(curTrain)
                else:
                    placed_trains.append(curTrain)
            elif data[0][0] == "P":
                passenger = Passengers(data[0], int(
                    data[3]), int(data[4].replace("\\n", "")))
                for station in stations:
                    if station.id == data[1]:
                        passenger.depatureStation = station
                    elif station.id == data[2]:
                        passenger.destinationStation = station
                passengers.append(passenger)

def write_output():
    file = open("output.txt", "w")
    file.close()
    for train in trains:
        train.write()
    for passenger in passengers:
        passenger.write()
#endregion

#region Lines graph
def build_lines_graph():
    for x in stations:
        lines_graph.add_node(x.id)
    for line in lines:
        lines_graph.add_edge(
            line.stations[0].id, line.stations[1].id, weight=line.length, attr=line.id)


def draw_lines_graph():
    # Debug output um Graph zu zeichnen
    nx.draw(lines_graph, with_labels=True)
    plt.show()
#endregion

#region Route generator
#region Route calculation
def calculate_route():
    for passenger in passengers:
        routes.append([shortest_path(lines_graph, source=passenger.depatureStation.id,
                      target=passenger.destinationStation.id), passenger.groupSize, passenger.targetTime, passenger.id])


def sort_routes_by_length():
    routes.sort(key=lambda x: (len(x[0]), -x[2]), reverse=True)


def pattern_matching():
    comparing_route = routes[0][0]
    matching_routes = []
    matching_routes.append(routes[0])
    for i in range(1, len(routes)):
        ix = 0
        current_route = routes[i][0]
        for j in range(0, len(comparing_route)):
            if (comparing_route[j] == current_route[ix]):
                ix += 1
                j += 1
            else:
                ix = 0
                j += 1
            if (ix == len(current_route)):
                matching_routes.append(routes[i])
                break
            elif(len(current_route)-ix>len(comparing_route)-j):
                break
    return matching_routes
#endregion

#region Find possible trains
def check_wildcard_trains():
    possible_trains = []
    for train in wildcard_trains:
        possible_trains.append(train)
    return possible_trains


def check_for_placed_trains(station):
    placed_trains.sort(key=lambda x: x.time_needed)
    possible_trains = []
    for train in placed_trains:
        if(train.endStation == None):
            if(train.currentStation.id == station.id):
                possible_trains.append(train)
        else:
            if(train.endStation.id == station.id):
                possible_trains.append(train)
    return possible_trains


def check_for_nearest_placed_train(station):
    shortest_distance = inf
    nearest_train = None
    placed_trains.sort(key=lambda x: x.time_needed)
    for train in placed_trains:
        distance = shortest_path_length(
            lines_graph, source=train.currentStation.id, target=station.id, weight="weight")
        if(train.time_needed+math.ceil(distance/train.speed) < shortest_distance):
            shortest_distance = train.time_needed + \
                math.ceil(distance/train.speed)
            nearest_train = train
    return nearest_train


def determine_possible_trains_for_route(start_node):
    possible_trains = check_for_placed_trains(start_node)
    if(isEmpty(possible_trains)):
        possible_trains = check_wildcard_trains()
    if(isEmpty(possible_trains)):
        possible_trains.append(check_for_nearest_placed_train(start_node))
    possible_trains.sort(key=lambda x: x.capacity)
    return possible_trains
#endregion

#region Route assignment
def calculate_approximate_time_needed(train, routes, start_station, end_station):
    length = shortest_path_length(
        lines_graph, source=start_station.id, target=end_station.id, weight="weight")
    final_stations = []
    for route in routes:
        final_stations.append(route[0][len(route[0])-1])
    stop_count = len(set(final_stations))
    return math.ceil(length / train.speed) + stop_count

def generate_final_route(matching_routes, current_capacity, max_capacity):
    final_route = []
    for route in matching_routes:
        if((current_capacity+route[1]) <= max_capacity):
            final_route.append(route)
            current_capacity+=route[1]
    return final_route


def determine_best_train_for_capacity(trains, capacity):
    for train in trains:
        if(train.capacity >= capacity):
            return train

def modify_train_route(train,route,passengers):
    for station in route:
        train.path.append(get_station_by_id(station))
    train.passengers+=(passengers)

def choose_wildcard_train(train,start_station):
    if(train in wildcard_trains):
        wildcard_trains.remove(train)
        train.startingPosition = start_station
        train.currentStation = start_station
        placed_trains.append(train)

def add_transition_route(train,start_station,end_station):
    transition_stations = shortest_path(lines_graph, source=start_station.id, target=end_station)
    train.time_needed+=calculate_approximate_time_needed(train,[],start_station,get_station_by_id(end_station))
    if(not isEmpty(train.path)):
        train.path.pop()
        train.passengers.pop()
    for station in transition_stations:
        train.path.append(get_station_by_id(station))
        train.passengers.append("")

def choose_train(train,time_needed,start_station,end_station,final_route):
    passenger_array=build_passenger_array(final_route)
    main_route=final_route[0][0]

    choose_wildcard_train(train,start_station)
    
    if (train.endStation==None):
        if (train.currentStation.id==main_route[0]):
            modify_train_route(train,main_route,passenger_array)
        else:
            add_transition_route(train,train.currentStation,main_route[0])
            train.path.pop()
            train.passengers.pop()
            modify_train_route(train,main_route,passenger_array)
    elif (train.endStation.id==main_route[0]):
        #remove last station from train's path and passengers, because it is equal to the first in the new route and passenger_array
        train.path.pop()
        train.passengers.pop()
        modify_train_route(train,main_route,passenger_array)
    else:
        add_transition_route(train,train.endStation,main_route[0])
        train.path.pop()
        train.passengers.pop()
        modify_train_route(train,main_route,passenger_array)

    train.time_needed+=time_needed
    train.endStation=end_station

def clear_assigned_routes(final_route):
    for route in final_route:
        if(route in routes):
            routes.remove(route)


def build_passenger_array(final_route):
    passengers = []
    for i in range(0, len(final_route[0][0])):
        station_passengers = []
        for route in final_route:
            if final_route[0][0][i] == route[0][0]:
                station_passengers.append(get_passenger_by_id(route[3]))
        passengers.append(station_passengers)
    return passengers
#endregion

def route_generation():
    final_route = []
    chosen_train = None
    current_capacity = 0

    #get route and matching subroutes
    matching_routes=pattern_matching()
    print("New route")
    print(matching_routes)
    
    #get start-/endstation
    start_station=get_station_by_id(matching_routes[0][0][0])
    end_station=get_station_by_id(matching_routes[0][0][len(matching_routes[0][0])-1])

    # get trains nearby or at start_station
    possible_trains = determine_possible_trains_for_route(start_station)

    # add father route (longest route) to final route
    final_route.append(matching_routes[0])

    # add passengers from father route to capacity count
    current_capacity += matching_routes[0][1]
    # remove father route from matching_routes
    matching_routes.remove(matching_routes[0])
    # sort matching_routes by group size
    matching_routes.sort(key=lambda x: x[2]*x[1])
    #get train with most capacity (possible_trains are sorted by capacity)
    max_capacity=possible_trains[len(possible_trains)-1].capacity
    #add matching_routes to final_routes based on available capacity
    final_route+=generate_final_route(matching_routes,current_capacity,max_capacity)
    #get best train for needed route capacity
    chosen_train=determine_best_train_for_capacity(possible_trains,current_capacity)
    
    #calculate time train needs for the route (approximately)
    time_needed=calculate_approximate_time_needed(chosen_train,final_route,start_station,end_station)
    
    choose_train(chosen_train,time_needed,start_station,end_station,final_route)

    clear_assigned_routes(final_route)

    #Max Capacity Analyse verfeinern, da zwischendurch ja auch Passagiere aussteigen
#endregion

#region Tick simulation
def move_train(train):
    #check if train is on line
    if(train.line == None):
        #if train is not on line and has path
        if(len(train.path) > 1):
            #get line
            lineId = lines_graph.get_edge_data(
                train.path[0].id, train.path[1].id)["attr"]
            line = get_line_by_id(lineId)
            #check if line has capacity free
            if(line.capacity > 0):
                #handle capacity
                line.capacity -= 1
                train.currentStation.capacity += 1
                #assign train to line
                train.currentStation = None
                train.line = line
                train.addAction(simulationTime.currentTick,
                                "Depart", train.line.id)
                move_train_on_line(train)
    else:
        #if train is on line -> move train
        move_train_on_line(train)


def move_train_on_line(train):
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


def move_trains():
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
                            simulationTime.currentTick, "Detrain")
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
                                simulationTime.currentTick, "Board", train.id)
                            train.boardedPassengers.append(passenger)
                        train.passengers[0] = []
                    elif(not hasDetrainedPassengers):
                        #else move train to next station
                        move_train(train)
                else:
                    #else move train to next station
                    move_train(train)
            else:
                #else move forward train to target station
                move_train(train)
        else:
            #detrain passengers on final station of train
            newPassengers = []
            for passenger in train.boardedPassengers:
                if(train.currentStation == passenger.destinationStation):
                    passenger.addAction(simulationTime.currentTick, "Detrain")
                else:
                    newPassengers.append(passenger)
            train.boardedPassengers = newPassengers
#endregion

#region Utils
def get_station_by_id(id):
    for i in range(0, len(stations)):
        if(stations[i].id == id):
            return stations[i]


def get_passenger_by_id(id):
    for i in range(0, len(passengers)):
        if(passengers[i].id == id):
            return passengers[i]


def get_line_by_id(id):
    for line in lines:
        if (line.id == id):
            return line


def isEmpty(list):
    if(len(list) == 0):
        return True
    else:
        return False

def get_overall_delay():
    delay = 0
    for passanger in passengers:
        if(passanger.delay > 0):
            delay += passanger.delay
    print("Gesamtverspätung: ", delay)

def initializeCurrentStations():
    for train in trains:
        train.currentStation=get_station_by_id(train.startingPosition)

def printTrainPassengerAssignment():
    for train in trains:
        print(train.id,": ",train.time_needed)
        pathString=""
        for station in train.path:
            if(station!=None):
                pathString+=station.id+" "
        print(pathString)
        passengersString=""
        for passengers_station in train.passengers:
            passengersString+="["
            for passenger in passengers_station:
                passengersString+=passenger.id+" "
            passengersString+="]"
        print(passengersString)
#endregion

#region Main
if __name__ == "__main__":
    load_input()
    build_lines_graph()
    # draw_lines_graph()
    initializeCurrentStations()
    calculate_route()
    sort_routes_by_length()
    
    while(len(routes)>0):
        route_generation()
        print(len(routes))

    printTrainPassengerAssignment()

    passengersAvailable = True
    while (passengersAvailable):
        move_trains()
        simulationTime.tick()
        passengersAvailable = False
        for passenger in passengers:
            if(not passenger.finished):
                # print(passenger.id)
                passengersAvailable = True
                break

    write_output()
    get_overall_delay()
#endregion