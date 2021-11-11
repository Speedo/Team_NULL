class Station:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity

    def toString(self):
        return f"ID: {self.id}, capacity: {self.capacity}"