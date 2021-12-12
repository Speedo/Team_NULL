import networkx as nx
import numpy as np
from classes.passengers import Passengers
from classes.train import Train
from networkx.algorithms.shortest_paths.generic import shortest_path_length

class Rating:
    def __init__(self, passengers, trains, graph):
        self.passengers = passengers
        self.trains = trains
        self.ratings = np.empty([len(passengers), len(trains)])
        self.graph = graph
    
    def calculateRating(self, passenger, train):
        if train.startingStation is not None:
            rating = passenger.targetTime
            rating -= shortest_path_length(self.graph, source=train.startingStation.id, target=passenger.depatureStation.id, weight="weight") * train.speed
            rating -= shortest_path_length(self.graph, source=passenger.depatureStation.id, target=passenger.destinationStation.id, weight="weight") * train.speed
            return rating

    def findRating(self):
        for i in range (0, len(self.passengers)-1):
            for j in range(0, len(self.trains)-1):
                self.ratings[i][j] = self.calculateRating(self.passengers[i], self.trains[j])
        print (self.ratings)


