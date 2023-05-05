class State:
    def __init__(self, pacmanNode, ghostDirection, pelletDirection, availableActions, isInFreight, closestGhostDistance):
        self.pacmanNode = pacmanNode
        self.ghostDirection = ghostDirection
        self.pelletDirection = pelletDirection
        self.availableActions = availableActions
        self.isInFreight = isInFreight
        self.closestGhostDistance = closestGhostDistance