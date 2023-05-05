import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from QLearning import State, QValueStore

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.learntDirection = STOP

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
        # direction = self.getValidKey()
        direction = self.getDirection()
        if self.overshotTarget():
            # print("Overshot target")
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            
            closestPelletNode = self.getClosestPellet()
            closestGhostNode= self.getClosestGhost()
            closestPelletDirection = self.findEntityDirection
            state = State(self.node, )

            self.target = self.getNewTarget(direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

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

    def getClosestPellet(self):
        pass

    def getClosestGhot(self):
        pass

    def findEntityDirection(self, node, entity):
        xDistance = abs(entity.position.x - node.position.x)
        yDistance = abs(entity.position.y - node.position.y)

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