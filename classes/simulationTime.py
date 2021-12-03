class SimulationTime():
    def __init__(self):
        self.currentTick = 0
        self.tickMultiplier = 1

    def tick(self):
        self.currentTick += self.tickMultiplier

    def setCurrentTick(self, currentTick):
        self.currentTick = currentTick

    def getCurrentTick(self):
        return self.currentTick

    def setTickMultiplier(self, tickMultiplier):
        self.tickMultiplier = tickMultiplier

    def getTickMultiplier(self):
        return self.tickMultiplier
