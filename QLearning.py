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
        key = str(state.ghostDirection) + str(state.pelletDirection) + str(state.availableActions) + str(action)
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

class ReinforcementProblem:
    def __init__(self):
        self.nodeGroup = NodeGroup("maze1.txt")

    # Choose a random starting state for the problem.
    def getRandomState(self, iteration):
        # pacmanNode = None
        # while(pacmanNode == None):
        #     pacmanNode = random.choice(list(self.nodeGroup.nodesLUT.values()))
        nodeKeys = list(self.nodeGroup.nodesLUT.keys())
        pacmanNode = self.nodeGroup.nodesLUT[nodeKeys[iteration % len(nodeKeys)]]
        randomState = State(pacmanNode, None, None, None)
        availableActions = self.getAvailableActions(randomState)
        randomState.ghostDirection = random.choice(availableActions)
        randomState.pelletDirection = random.choice(availableActions)
        randomState.availableActions = availableActions
        return randomState
        

    # Get the available actions for the given state.
    def getAvailableActions(self, state):
        actions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if state.pacmanNode.neighbors[key] is not None:
                actions.append(key)
        return actions

    # Take the given action and state, and return
    # a pair consisting of the reward and the new state.
    def takeAction(self, state, action):
        newState = self.getRandomState(0)
        
        reward = 0
        if state.ghostDirection == action:
            reward -= 5
        # if state.ghostDirection != action:
        #     reward += 1
        if state.pelletDirection == action:
            reward += 4

        return reward, newState
        

class QLearner:
    def __init__(self):
        # The store for Q-values, we use this to make decisions based on # the learning.
        self.store = QValueStore()

    # Updates the store by investigating the problem.
    def QLearning(self, problem, alpha, gamma, rho, nu):
        # Get a starting state.
        state = problem.getRandomState(0)

        # Repeat a number of times.
        for i in range(ITERATIONS):
            if i % 500 == 0:
                self.savePolicy(i)
            # Pick a new state every once in a while.
            if random.random() < nu:
                state = problem.getRandomState(i)

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

    # Loads a Q-table.
    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.store.qStore = pickle.load(fr)
        fr.close()
        return self.store.qStore

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
    
    rho=0.3
    alpha=1.0
    gamma=0
    nu = 1.0    # Always pick a random state for a new iteration

    if TRAINING:
        problem = ReinforcementProblem()
        qLearner = QLearner()
        qLearner.QLearning(problem, alpha, gamma, rho, nu)
    else:
        qLearner = QLearner()
        loadedStore = qLearner.loadPolicy("felixController")
        qLearner.store.qStore = loadedStore
        game = GameController()
        game.startGame()
        for q in loadedStore.keys():
            print(q)
        # print(len(loadedStore.keys()))
        game.pacman.qValueStore = qLearner.store
        game.update()
        while True:
            game.update()