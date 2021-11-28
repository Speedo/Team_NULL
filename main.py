from classes.line import Line
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
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
    ############### Graph #################
    #######################################
    #######################################
"""
def build_graph()_
    G = nx.Graph()
    for x in stations:
        G.add_node(x.id)
    for line in lines:
        G.add_edge(line.stations[0].id, line.stations[1].id, weight=line.length)
        
    nx.draw(G, with_labels=True)
    plt.show()

"""
    #######################################
    #######################################
    ############### Main ##################
    #######################################
    #######################################
"""
if __name__ == "__main__":
    load_input()
    #write_output()
    build_graph()