from nodes import NodeGroup
from constants import *
import random
import pickle
from run import GameController
from state import State
import sys

class QValueStore:
    def __init__(self):
        self.qStore = {}

    def constructKey(self, state, action):
        key = str(state.ghostDirections) + str(state.pelletDirection) + str(state.availableActions) + str(state.isInFreight) + str(action)
        return key

    def getQValue(self, state, action):
        key = self.constructKey(state, action)
        if key not in self.qStore.keys():
                self.storeQValue(state, action, 0)
        return self.qStore[key]

    def getBestAction(self, state):
        actions = state.availableActions
        result = {}
        for action in actions:
            result[action] = self.getQValue(state, action)
        return max(result, key=result.get)

    def storeQValue(self, state, action, value):
        key = self.constructKey(state, action)
        self.qStore[key] = value

    # Loads a Q-table.
    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.qStore = pickle.load(fr)
        fr.close()

class ReinforcementProblem:
    def __init__(self):
        self.game = GameController()
        self.lastScore = 0

    # Choose a random starting state for the problem.
    def getRandomState(self):
        self.game.restartGame()
        self.game.pacman.setStartNode(self.getRandomNode())
        for ghost in self.game.ghosts.ghosts:
            ghost.setStartNode(self.getRandomNode())
        self.game.pause.paused = False
        
        self.lastScore = 0

        return self.game.pacman.compileState()
        
    def getRandomNode(self):
        nodeKeys = list(self.game.nodes.nodesLUT.keys())
        return self.game.nodes.nodesLUT[random.choice(nodeKeys)]

    # Get the available actions for the given state.
    def getAvailableActions(self, state):
        return state.availableActions

    # Take the given action and state, and return
    # a pair consisting of the reward and the new state.
    def takeAction(self, state, action):
        self.game.pacman.learntDirection = action
        self.game.update()
        newState = self.game.pacman.compileState()
        self.game.pause.paused = False
        # if self.game.pacman.diedThisIteration is True:
        #     reward = -100
        #     self.game.pacman.diedThisIteration = False
        # else:
        #     reward = self.game.score - self.lastScore
        
        # self.lastScore = self.game.score

        # reward = 0
        # for i in range(len(state.ghostDirections)):
        #     if state.ghostDirections[i] == action:
        #         if state.isInFreight:
        #             reward += 20
        #         else:
        #             reward -= 20
        # if state.pelletDirection == action:
        #     reward += 10

        reward = 0
        if state.ghostDirections != None and state.ghostDirections == action:
            if state.isInFreight:
                reward += 20
            else:
                reward -= 20
        if state.pelletDirection == action:
            reward += 10
    

        return reward, newState
        

class QLearner:
    def __init__(self):
        # The store for Q-values, we use this to make decisions based on # the learning.
        self.store = QValueStore()

    # Updates the store by investigating the problem.
    def QLearning(self, problem, alpha, gamma, rho, nu):
        # Get a starting state.
        state = problem.getRandomState()

        # Repeat a number of times.
        # for i in range(ITERATIONS):
        i = 0
        while True:
            if i % 10000 == 0:
                self.savePolicy(i)
            i += 1
            # Pick a new state every once in a while.
            if random.random() < nu:
                state = problem.getRandomState()

            # Get the list of available actions.
            actions = problem.getAvailableActions(state)

            # Should we use a random action this time?
            if random.random() < rho:
                action = random.choice(actions)
            # Otherwise pick the best action.
            else:
                action = self.store.getBestAction(state)
            
            reward, newState = problem.takeAction(state, action)
            
            # Get the current q from the store.
            Q = self.store.getQValue(state, action)

            # Get the q of the best action from the new state.
            maxQ = self.store.getQValue(newState, self.store.getBestAction(newState))

            # Perform the q learning.
            Q = (1 - alpha) * Q + alpha * (reward + gamma * maxQ)

            # Store the new Q-value.
            self.store.storeQValue(state, action, Q)

            # And update the state.
            state = newState

        # Saves the Q-table.
    def savePolicy(self, iterations):
        fileName = "felixController"
        fw = open(fileName, 'wb')
        pickle.dump(self.store.qStore, fw)
        fw.close()

        with open('training_log.txt', 'w') as f:
            f.write(fileName + " - Completed Training Iterations: " + str(iterations))
        print(fileName + " - Completed Training Iterations: " + str(iterations))

if __name__ == "__main__":
    #### PARAMETERS:
    # ALPHA -> Learning Rate
    # controls how much influence the current feedback value has over the stored Q-value.

    # GAMMA -> Discount Rate
    # how much an action’s Q-value depends on the Q-value at the state (or states) it leads to.

    # RHO -> Randomness of Exploration
    # how often the algorithm will take a random action, rather than the best action it knows so far.

    # NU: The Length of Walk
    # number of iterations that will be carried out in a sequence of connected actions.

    if TRAINING:
        rho=0.2
        alpha=0.3
        gamma=0.75
        nu = 0.001  
        problem = ReinforcementProblem()
        qLearner = QLearner()
        qLearner.store.loadPolicy("felixController")
        qLearner.QLearning(problem, alpha, gamma, rho, nu)
    else:
        qValueStore = QValueStore()
        qValueStore.loadPolicy("felixController")
        game = GameController()
        game.qValueStore = qValueStore
        game.startGame()
        while(True):
            game.update()