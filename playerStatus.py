import numpy as np

class PlayerStatus:
    def __init__(self):
        self.ownPos = np.array([])
        self.ownPosXY = [9999, 9999, 9999]
        self.othersStatus = {}

    def getDistance(self, p1):
        if np.size(self.ownPos) == 0:
            return -9999
        dist = np.linalg.norm(self.ownPos / 100000 - p1 / 100000) / 2
        return dist