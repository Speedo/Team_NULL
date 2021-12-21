from networkx.generators.expanders import paley_graph
from numpy import Inf, inf, true_divide
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
"""
    #######################################
    #######################################
    ############# Variables ###############
    #######################################
    #######################################
"""
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

"""
    #######################################
    #######################################
    ############### Input #################
    #######################################
    #######################################
"""


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


"""
    #######################################
    #######################################
    ############### Output ################
    #######################################
    #######################################
"""


def write_output():
    file = open("output.txt", "w")
    file.close()
    for train in trains:
        train.write()
    for passenger in passengers:
        passenger.write()


"""
    #######################################
    #######################################
    ############ Lines Graph ##############
    #######################################
    #######################################
"""


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


"""
    #######################################
    #######################################
    ###### Group and Sort Passengers ######
    #######################################
    #######################################
"""


def group_passengers_by_DepartureStation():
    for station in stations:
        for passenger in passengers:
            if passenger.depatureStation == station:
                station.addPassenger(passenger)


def sort_passengers_by_arrivalTime():
    for station in stations:
        station.passengers.sort(key=lambda x: x.targetTime)


def print_passengers(station):
    for passenger in station.passengers:
        print("passenger: ")
        print(passenger.id, passenger.targetTime,
              passenger.destinationStation.id)


"""
    #######################################
    #######################################
    ######## Group and Sort Trains ########
    #######################################
    #######################################
"""


def group_trains_by_startingPosition():
    for station in stations:
        for train in trains:
            if train.startingPosition == station.id:
                station.addTrain(train)


def sort_trains_by_speed():
    for station in stations:
        station.trains.sort(key=lambda x: x.speed)


"""
    #######################################
    #######################################
    ############### Delay #################
    #######################################
    #######################################
"""


def calculate_delay(targetTime: int, speed: float, length: float, tick: int):
    return targetTime - (length / speed + tick)


def get_overall_delay():
    delay = 0
    for passanger in passengers:
        if(passanger.delay > 0):
            delay += passanger.delay
    print("Gesamtverspätung: ", delay)


"""
    #######################################
    #######################################
    ######## Fixing Train Station #########
    #######################################
    #######################################
"""

def initializeCurrentStations():
    for train in trains:
        train.currentStation=get_station_by_id(train.startingPosition)


"""
    #######################################
    #######################################
    ########### Route Comparer ############
    #######################################
    #######################################
"""


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


def calculate_approximate_time_needed(train, routes, start_station, end_station):
    length = shortest_path_length(
        lines_graph, source=start_station.id, target=end_station.id, weight="weight")
    final_stations = []
    for route in routes:
        final_stations.append(route[0][len(route[0])-1])
    stop_count = len(set(final_stations))
    return math.ceil(length / train.speed) + stop_count


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


def generate_final_route(matching_routes, max_capacity):
    times = {}
    for station in matching_routes[0][0]:
        times[station]=0
    final_route = []
    for route in matching_routes:
        hasCapacity = True
        curTimes = times.copy()
        for i in range(0,len(route[0])-1):
            times[route[0][i]]+=route[1]
            if(times[route[0][i]]>max_capacity):
                times = curTimes
                hasCapacity = False
                break

        if(hasCapacity):
            final_route.append(route)
    return [max(times.values()),final_route]

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


def route_generation():
    final_route = []
    chosen_train = None

    #get route and matching subroutes
    matching_routes=pattern_matching()
    
    #get start-/endstation
    start_station=get_station_by_id(matching_routes[0][0][0])
    end_station=get_station_by_id(matching_routes[0][0][len(matching_routes[0][0])-1])

    # get trains nearby or at start_station
    possible_trains = determine_possible_trains_for_route(start_station)

    # sort matching_routes by group size
    matching_routes.sort(key=lambda x: x[2]*x[1])
    #get train with most capacity (possible_trains are sorted by capacity)
    max_capacity=possible_trains[len(possible_trains)-1].capacity
    #add matching_routes to final_routes based on available capacity
    routeData = generate_final_route(matching_routes,max_capacity)
    current_capacity=routeData[0]
    final_route+=routeData[1]
    #get best train for needed route capacity
    chosen_train=determine_best_train_for_capacity(possible_trains,current_capacity)
    
    #calculate time train needs for the route (approximately)
    time_needed=calculate_approximate_time_needed(chosen_train,final_route,start_station,end_station)
    
    choose_train(chosen_train,time_needed,start_station,end_station,final_route)

    clear_assigned_routes(final_route)

    #Max Capacity Analyse verfeinern, da zwischendurch ja auch Passagiere aussteigen

def move_train(train):
    if(train.line == None):
        if(len(train.path) > 1):
            lineId = lines_graph.get_edge_data(
                train.path[0].id, train.path[1].id)["attr"]
            line = get_line_by_id(lineId)
            # Wenn Line frei befahren
            if(line.capacity > 0):
                line.capacity -= 1
                train.currentStation.capacity += 1
                train.currentStation = None
                train.line = line
                train.addAction(simulationTime.currentTick,
                                "Depart", train.line.id)
                move_train_on_line(train)
    else:
        move_train_on_line(train)


def move_train_on_line(train):
    # Zug ziehen
    train.progress += 1/(train.line.length/train.speed)
    if(train.progress >= 1 and train.path[0].capacity > 0):
        # Station erreicht
        train.path.pop(0)
        train.currentStation = train.path[0]
        train.currentStation.capacity -= 1
        train.progress = 0
        train.line.capacity += 1
        train.passengers.pop(0)
        train.line = None


def move_trains():
    for train in trains:
        # Check if train has path
        if(len(train.path) > 1):
            if(train.currentStation == train.path[0]):
                # Passagiere an dieser Position einsteigen
                hasDetrainedPassengers = False
                newPassengers = []
                for passenger in train.boardedPassengers:
                    if(train.currentStation == passenger.destinationStation):
                        passenger.addAction(
                            simulationTime.currentTick, "Detrain")
                        # train.boardedPassengers.remove(passenger)
                        hasDetrainedPassengers = True
                    else:
                        newPassengers.append(passenger)
                train.boardedPassengers = newPassengers
                if(len(train.passengers) > 0):
                    if(len(train.passengers[0]) > 0):
                        # Passagiere einsteigen lassen
                        for passenger in train.passengers[0]:
                            passenger.addAction(
                                simulationTime.currentTick, "Board", train.id)
                            train.boardedPassengers.append(passenger)
                        train.passengers[0] = []
                    elif(not hasDetrainedPassengers):
                        # Oder weiterfahren (Überprüfen ob Strecke frei)
                        move_train(train)
                else:
                    # Oder weiterfahren (Überprüfen ob Strecke frei)
                    move_train(train)
            else:
                # Richtung train.path[0] fahren (Überprüfen ob Strecke frei)
                move_train(train)
        else:
            newPassengers = []
            for passenger in train.boardedPassengers:
                if(train.currentStation == passenger.destinationStation):
                    passenger.addAction(simulationTime.currentTick, "Detrain")
                else:
                    newPassengers.append(passenger)
            train.boardedPassengers = newPassengers


"""
    #######################################
    #######################################
    ############### Main ##################
    #######################################
    #######################################
"""
if __name__ == "__main__":
    load_input()
    group_passengers_by_DepartureStation()
    group_trains_by_startingPosition()
    sort_passengers_by_arrivalTime()
    sort_trains_by_speed()
    build_lines_graph()
    # draw_lines_graph()
    fixTrainStationLinks()
    calculate_route()
    sort_routes_by_length()
    
    while(len(routes)>0):
        route_generation()
    
    for train in trains:
        print(train.id,": ",train.time_needed)
        path=""
        for station in train.path:
            if(station!=None):
                path+=station.id+" "
        print(path)
        passengersString=""
        for passengers_station in train.passengers:
            passengersString+="["
            for passenger in passengers_station:
                passengersString+=passenger.id+" "
            passengersString+="]"
        print(passengersString)

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