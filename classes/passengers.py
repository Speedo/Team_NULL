from classes.action import Action


class Passengers:
    def __init__(self, id, groupSize, targetTime):
        self.id = id
        self.depatureStation = ""
        self.destinationStation = ""
        self.groupSize = groupSize
        self.targetTime = targetTime
        self.delay = 0
        self.train = ""
        self.finished = False
        self.actions = []

    def addAction(self, time, action, target=""):
        self.actions.append(Action(time, action, target))
        if(action == "Detrain"):
            self.delay = self.targetTime-time
            self.finished = True

    def write(self):
        file = open("output.txt", "a")
        file.write(f"[Passenger:{self.id}]\n")
        for action in self.actions:
            file.write(action.toString())
        file.write("\n")
        file.close()
