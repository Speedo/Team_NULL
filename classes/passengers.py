class Passengers:
    def __init__(self, id, groupSize, targetTime):
        self.id = id
        self.depatureStation = ""
        self.destinationStation = ""
        self.groupSize = groupSize
        self.targetTime = targetTime
        self.train = ""

    def toString(self):
        return f"ID: {self.id}, depatureStation: {self.depatureStation.id}, destinationStation: {self.destinationStation.id}, groupSize: {self.groupSize}, targetTime: ${self.targetTime}"