class Bomb:
    def __init__(self, row, col, owner, timer=20, power=1):
        self.row = row
        self.col = col
        self.owner = owner
        self.timer = timer
        self.power = power

    def tick(self):
        self.timer -= 1

    def has_exploded(self):
        return self.timer <= 0
