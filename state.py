class State:
    def __init__(self, pacmanNode, ghostDirections, pelletDirection, availableActions, isInFreight, closestGhost):
        self.pacmanNode = pacmanNode
        self.ghostDirections = ghostDirections
        self.pelletDirection = pelletDirection
        self.availableActions = availableActions
        self.isInFreight = isInFreight
        self.closestGhost = closestGhost