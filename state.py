class State:
    def __init__(self, ghostDirections, pelletDirection, availableActions, isInFreight):
        self.ghostDirections = ghostDirections
        self.pelletDirection = pelletDirection
        self.availableActions = availableActions
        self.isInFreight = isInFreight