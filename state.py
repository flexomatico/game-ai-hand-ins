class State:
    def __init__(self, pacmanNode, ghostDirection, pelletDirection, availableActions):
        self.pacmanNode = pacmanNode
        self.ghostDirection = ghostDirection
        self.pelletDirection = pelletDirection
        self.availableActions = availableActions