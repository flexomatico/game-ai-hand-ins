import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from state import State
import sys

class Pacman(Entity):
    def __init__(self, node, pelletList):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.pelletList = pelletList
        self.ghosts = None
        self.qValueStore = None
        self.learntDirection = STOP
        self.diedThisIteration = False

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
        self.diedThisIteration = True

    def update(self, dt):
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        # direction = self.getValidKey()
        # direction = self.getDirection()
        if self.overshotTarget():
            # print("Overshot target")
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            
            if TRAINING:
                self.direction = self.learntDirection
            else:
                state = self.compileState()
                self.direction = self.qValueStore.getBestAction(state)
            self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        # else: 
        #     if self.oppositeDirection(direction):
        #         self.reverseDirection()

    def getDirection(self):
        return self.learntDirection 

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def getClosestEntity(self, entityList):
        minDistance = sys.maxsize
        closestEntity = None
        for entity in entityList:
            entityDistance = self.getEntityManhattanDistance(entity)

            if entityDistance < minDistance:
                minDistance = entityDistance
                closestEntity = entity
        
        return minDistance, closestEntity
    
    def getEntityDistance(self, entity):
        return (entity.position - self.node.position).magnitude()
    
    def getEntityManhattanDistance(self, entity):
        return abs(entity.position.x - self.node.position.x) + abs(entity.position.y - self.node.position.y)
    
    def compileState(self):
        pelletDistance, closestPellet = self.getClosestEntity(self.pelletList)
        ghostDistance, closestGhost = self.getClosestEntity(self.ghosts)
        self.goal = closestPellet.position
        closestPelletDirection = self.goalDirection(self.validDirections())
        self.goal = closestGhost.position
        if ghostDistance < 80.0:
            closestGhostDirection = self.goalDirection(self.validDirections())
        else:
            closestGhostDirection = None
        # ghostDirections = []
        # for ghost in self.ghosts:
        #     ghostDistance = self.getEntityManhattanDistance(ghost)
        #     # print(ghostDistance)
        #     if ghostDistance < 130:
        #         self.goal = ghost.position
        #         ghostDirection = self.goalDirection(self.validDirections())
        #         ghostDirections.append(ghostDirection)
        isInFreight = closestGhost.mode.current == FREIGHT or closestGhost.mode.current == SPAWN
        return State(closestGhostDirection, closestPelletDirection, self.validDirections(), isInFreight)