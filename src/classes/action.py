class Action:
    def __init__(self, time, action, target=""):
        self.time = time
        self.action = action
        self.target = target

    def toString(self):
        if self.target == "":
            return f"{self.time} {self.action}\n"
        else:
            return f"{self.time} {self.action} {self.target}\n"
