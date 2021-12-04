from classes.line import Line
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
from classes.simulationTime import SimulationTime
import networkx as nx
import matplotlib.pyplot as plt

"""
    #######################################
    #######################################
    ############# Variables ###############
    #######################################
    #######################################
"""
trains = []
stations = []
lines = []
passengers = []
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
                stations.append(Station(data[0], int(data[1].replace("\\n", ""))))
            elif data[0][0] == "L":
                line = Line(data[0], float(data[3]),
                            int(data[4].replace("\\n", "")))
                for station in stations:
                    if(station.id == data[1] or station.id == data[2]):
                        line.addStation(station)
                lines.append(line)
            elif data[0][0] == "T":
                trains.append(Train(data[0], data[1], float(
                    data[2]), int(data[3].replace("\\n", ""))))
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
        lines_graph.add_edge(line.stations[0].id, line.stations[1].id, weight=line.length)
    
def draw_lines_graph():
    #Debug output um Graph zu zeichnen
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
        print(passenger.id, passenger.targetTime, passenger.destinationStation.id)

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

def calculate_delay(targetTime:int, speed:float, length:float, tick:int):
    return targetTime - (length / speed + tick)



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
    draw_lines_graph()
    #write_output()