from classes.action import Action


class Train:
    def __init__(self, id, startingPosition, speed, capacity, idletime):
        self.id = id
        self.startingPosition = startingPosition
        self.currentStation = None
        self.boardedPassengers = []
        self.speed = speed
        self.capacity = capacity
        self.actions = []
        self.line = None
        self.progress = 0
        self.timeNeeded = 0
        self.endStation = None
        self.path = []
        self.passengers = []
        self.idle = idletime
        self.finished = False

    def addAction(self, time, action, target):
        self.actions.append(Action(time, action, target))

    def write(self):
        output = ""
        output += f"[Train:{self.id}]\n"
        for action in self.actions:
            output += action.toString()
        output += "\n"
        return output