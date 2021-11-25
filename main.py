from classes.line import Line
from classes.passengers import Passengers
from classes.station import Station
from classes.train import Train
trains = []
stations = []
lines = []
passengers = []
"""
    #######################################
    #######################################
    ############### Input #################
    #######################################
    #######################################
"""
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
    Beispiel um Aktion einem Tain/Passenger hinzuzufügen
"""
#trains[0].addAction(0, "Start", "Test")
#trains[0].addAction(1, "Depart", "Test2")
#passengers[0].addAction(0, "Board", "Test")
#passengers[0].addAction(2, "Detrain")
"""
    #######################################
    #######################################
    ############### Output #################
    #######################################
    #######################################
"""
file = open("output.txt", "w")
file.close()
for train in trains:
    train.write()
for passenger in passengers:
    passenger.write()
