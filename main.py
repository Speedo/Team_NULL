from classes.line import Line
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
trains = []
stations = []
lines = []
passengers = []
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
                    passenger.depatureStation=station
                elif station.id == data[2]:
                    passenger.destinationStation = station
            passengers.append(passenger)

"""
    #######################################
    #######################################
    ########### Debug Outputs #############
    #######################################
    #######################################
"""
print("Stations")
for station in stations:
    print(station.toString())
print("Lines")
for line in lines:
    print(line.toString())
print("Trains")
for train in trains:
    print(train.toString())
print("Passengers")
for passenger in passengers:
    print(passenger.toString())
