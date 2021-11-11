class Train:
    def __init__(self, id, startingPosition, capacity, speed):
        self.id = id
        self.startingPosition = startingPosition
        self.speed = speed
        self.capacity = capacity
        self.passengers = []
        self.line = ""

    def toString(self):
        return f"ID: {self.id}, StartingPositon: {self.startingPosition}, Speed: {self.speed}, Capacity: {self.capacity}"
