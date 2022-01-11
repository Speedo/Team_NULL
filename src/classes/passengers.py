from classes.action import Action


class Passengers:
    def __init__(self, id, depatureStation, destinationStation, groupSize, targetTime):
        self.id = id
        self.depatureStation = depatureStation
        self.destinationStation = destinationStation
        self.groupSize = groupSize
        self.targetTime = targetTime
        self.delay = 0
        self.train = ""
        self.finished = False
        self.actions = []

    def addAction(self, time, action, target=""):
        self.actions.append(Action(time, action, target))
        if(action == "Detrain"):
            self.delay = time-self.targetTime
            self.finished = True

    def write(self):
        output = ""
        output += f"[Passenger:{self.id}]\n"
        for action in self.actions:
            output += action.toString()
        output += "\n"
        return output
