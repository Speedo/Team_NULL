import networkx as nx
import numpy as np
from passengers import Passengers
from train import Train
from networkx.algorithms.shortest_paths.generic import shortest_path_length

class Rating:
    def __init__(self, passengers, trains, graph):
        self.passengers = passengers
        self.trains = trains
        self.ratings = np.empty([len(passengers), len(trains)])
        self.graph = graph
    
    def calculateRating(self, passenger, train):
        rating = passenger.targetTime
        rating -= shortest_path_length(self.graph, source=train.startingPosition, target=passenger.departureStation) * train.speed
        rating -= shortest_path_length(self.graph, source=passenger.departureStation, target=passenger.destinationStation) * train.speed
        return rating

    def findRating(self):
        for i in self.passengers:
            for j in self.trains:
                self.ratings[i][j] = self.calculateRating(self.passengers[i], self.trains[j])
        print (self.ratings)


