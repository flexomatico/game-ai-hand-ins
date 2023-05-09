class State:
    def __init__(self, ghostDirections, pelletDirection, availableActions, isInFreight, closestGhost):
        self.ghostDirections = ghostDirections
        self.pelletDirection = pelletDirection
        self.availableActions = availableActions
        self.isInFreight = isInFreight
        self.closestGhost = closestGhost