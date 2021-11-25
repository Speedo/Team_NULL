from classes.action import Action


class Train:
    def __init__(self, id, startingPosition, capacity, speed):
        self.id = id
        self.startingPosition = startingPosition
        self.speed = speed
        self.capacity = capacity
        self.passengers = []
        self.actions = []
        self.line = ""

    def addAction(self, time, action, target):
        self.actions.append(Action(time, action, target))

    def write(self):
        file = open("output.txt", "a")
        file.write(f"[Train:{self.id}]\n")
        for action in self.actions:
            file.write(action.toString())
        file.write("\n")
        file.close()
