
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from pathfinder import *
import random
import numpy as np
import pickle

class State:
    def __init__(self, pelletDirection, firstGhostDirection):

        self.pelletDirection = pelletDirection
        self.firstGhostDirection = firstGhostDirection
        #self.secondGhostDirection = secondGhostDirection
    
    def GetKey(self):

        key = str(self.pelletDirection) + str(self.firstGhostDirection)
        #print(f"key: {key}")
        return key 


class Pacman(Entity):
    def __init__(self, node, nodes, pellets):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = STOP
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nodes = nodes
        self.pellets = pellets
        self.ghosts = []
        self.qValues = {}
        self.isEnd = False

    def UpdatePacman(self, node):
        self.node = node

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
            
        self.alive = False
        self.direction = STOP

    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        # actions = self.validDirections()
        # closestPellet = self.FindClosestPellet(self.node)
        # closestPelletDirection = self.FindEntityDirection(self.node, closestPellet)
        # state = State(closestPelletDirection)
        # direction = self.GetBestAction(actions, state)

        if self.overshotTarget():
            self.node = self.target
            #to make bestAction work
            actions = self.validDirections()
            closestPellet = self.FindClosestPellet(self.node)
            closestPelletDirection = self.FindEntityDirection(self.node, closestPellet)
            closestGhost = self.FindClosestGhost(self.node)
            if(closestGhost !=None):
                closestGhostDirection = self.FindEntityDirection(self.node, closestGhost)
            else:
                closestGhostDirection = STOP
            state = State(closestPelletDirection, closestGhostDirection)
            direction = self.GetBestAction(actions, state)

            # if self.node.neighbors[PORTAL] is not None:
            #     self.node = self.node.neighbors[PORTAL]

            self.target = self.getNewTarget(direction)

            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()


    def indexConverter(self, index):
        if index == UP:
            return 0
        elif index == DOWN:
            return 1
        elif index == LEFT:
            return 2
        elif index == RIGHT:
            return 3
        
    def GetBestAction(self, actions, state):

            bestValue = -9999
            for action in actions:
                
                key = state.GetKey() + str(action)
                if key not in self.qValues:
                    self.qValues[key] = 0
                currentValue = self.qValues[key]

                if currentValue > bestValue:
                    chosenAction = action
                    bestValue = currentValue
                

            return chosenAction

    def GetOneOfTheAction(self, actions):
        
        direction = random.choice(actions)
        return direction
    
    def ComputeReward(self, state, action):
        
        reward = 0.1
        
        if state.pelletDirection == action:
            reward = 0.7

        if state.firstGhostDirection == action:
            reward = reward - 1
        
        return reward
    
    def gameEnded(self, game):
        if game.lives <= 0 :
            self.isEnd = True
            self.finalScore = game.score
            return 0
        if game.level > self.level:
            return 1
        else:
            return None

    def TakeAction(self, state, action):
        
        #print(f"currentNode: {state.node}")
        self.target = self.getNewTarget(action)
        #print(f"targetNode: {self.target}")
        ghostDirection = self.GetRandomDirectionGhost()
        newState = State(random.choice(self.GetValidActions(self.target)), ghostDirection)
        self.UpdatePacman(self.target)
        
        reward = self.ComputeReward(state, action)
        return reward, newState
    
    def GetRandomDirection(self):
        directions = [UP, DOWN, LEFT, RIGHT]
        direction = random.choice(directions)
        return direction
    
    def GetRandomDirectionGhost(self):
        directions = [UP, DOWN, LEFT, RIGHT, STOP]
        direction = random.choice(directions)
        return direction

    def GetRandomState(self, node):

        pelletDirection = random.choice(self.GetValidActions(node))
        ghostDirection = self.GetRandomDirectionGhost()
        state = State(pelletDirection, ghostDirection)
        return state
    
    def GetRandomNode(self):
        node = random.choice(list(self.nodes.nodesLUT.values()))
        return node
        
    def qLearning(self):
        
        node = self.GetRandomNode()
        state = self.GetRandomState(node)

        for episode in range(10000):
            if episode % 1000 == 0:
                print("Episode: ", episode)
            if episode % 500 == 0:
                self.savePolicy()

            rand_nu = random.uniform(0,1)
            if rand_nu < NU: 
                node = self.GetRandomNode()
                state = self.GetRandomState(node)
            
            # Get the list of available actions. 
            actions = self.validDirections()
            #print(f"actions: {actions}")

            if random.uniform(0, 1) < RHO:
                action = self.GetOneOfTheAction(actions)
            else:
                action = self.GetBestAction(actions, state)
            
            #execute decided action, also update pacman position
            reward, newState = self.TakeAction(state, action)
                    
            # Get the current q from the store.
            key = state.GetKey() + str(action)
            if key not in self.qValues.keys():
                self.qValues[key] = 0
            Q = self.qValues[key]

            # Get the q of the best action from the new state.
            newActions = self.validDirections()
            newAction = self.GetBestAction(newActions, state)
            newKey = newState.GetKey() + str(newAction)
            if newKey not in self.qValues.keys():
                self.qValues[newKey] = 0
            maxQ = self.qValues[newKey]

            # Perform the q learning.
            Q = (1 - ALPHA) * Q + ALPHA * (reward + GAMMA * maxQ)

            # Store the new Q-value.
            self.qValues[key] = Q

            # And update the state.
            state = newState
        
        for keys,values in self.qValues.items():
            print(f"key/pelletDirection + action: {keys}")
            print(f"value: {values}")
        self.reset()
        #print(self.position)

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_RIGHT]:
            return

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None   
    
    def collideGhost(self, ghost):
        #return False
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
    
    def FindEntityDirection(self, node, entity):
        xDistance = abs(entity.position.x - node.position.x)
        yDistance = abs(entity.position.y - node.position.y)
        #print(f"xDistance: {xDistance}")
        #print(f"yDistance: {yDistance}")
        #print(f"pelletPosition: {pellet.position}")

        if(xDistance > yDistance):
            if(entity.position.x > node.position.x):
                direction = RIGHT
            else:
                direction = LEFT   
        else:
            if(entity.position.y > node.position.y):
                direction = DOWN
            else:
                direction = UP

        return direction
    
    def FindClosestPellet(self, node):
        minDistance = sys.maxsize
        chosenPellet = None

        for pellet in self.pellets.pelletList:
            distance = self.distance(pellet, node)

            if distance < minDistance:
                minDistance = distance
                chosenPellet = pellet

        chosenPellet.color = RED

        for pellet in self.pellets.pelletList:
            if pellet == chosenPellet:
                continue
            pellet.color = WHITE

        return chosenPellet

        
    def FindClosestGhost(self, node):
        minDistance = sys.maxsize
        chosenGhost = None

        for ghost in self.ghosts:
            distance = self.distance(ghost, node)
            #print(f"ghostDistance: {distance}")
            if(distance > 100):
                continue

            if ghost.mode == FREIGHT:
                print("freighted")
                continue

            if distance < minDistance:
                minDistance = distance
                chosenGhost = ghost

        return chosenGhost

        #print(f"key: {key}")
        #print(f"chosenPellet Position: {chosenPellet.position}")

    
    def AddGhost(self, ghost):
        self.ghosts.append(ghost)

    def distance(self, currentNode, endGoal):
        distance = abs(currentNode.position.x - endGoal.position.x) + abs(currentNode.position.y - endGoal.position.y) 

        return distance
    
    # Saves the Q-table.
    def savePolicy(self):
        fw = open('Qcontroller', 'wb')
        pickle.dump(self.qValues, fw)
        fw.close()

    # Loads a Q-table.
    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.qValues = pickle.load(fr)
        fr.close()
        

    

