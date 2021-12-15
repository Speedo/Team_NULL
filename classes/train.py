from classes.action import Action


class Train:
    def __init__(self, id, startingPosition, speed, capacity):
        self.id = id
        self.startingPosition = startingPosition
        self.currentStation = None
        self.boardedPassengers = []
        self.speed = speed
        self.capacity = capacity
        self.actions = []
        self.line = None
        self.progress = 0
        self.time_needed = 0
        self.endStation = None
        self.path = []
        self.passengers = []

    def addAction(self, time, action, target):
        self.actions.append(Action(time, action, target))

    def write(self):
        file = open("output.txt", "a")
        file.write(f"[Train:{self.id}]\n")
        for action in self.actions:
            file.write(action.toString())
        file.write("\n")
        file.close()
