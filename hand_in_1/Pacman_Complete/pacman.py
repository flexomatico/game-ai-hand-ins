import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from algorithms import dijkstra_or_a_star
from random import choice
from pellets import DebugPellet
import copy

class Pacman(Entity):
    def __init__(self, node, nodes, pelletLUT):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        # ======= HAND IN 1 MODIFICATION ===========
        self.directionMethod = self.goalDirectionDij
        self.nodes = nodes
        self.pelletLUT = pelletLUT
        self.debugPellet = DebugPellet(10, 10)
        # ==========================================

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
        # ======= HAND IN 1 MODIFICATION ===========
        #direction = self.getValidKey()
        directions = self.validDirections()
        #print(directions)
        direction = self.directionMethod(directions)
        #print(direction)
        # ==========================================
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

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

#############
    # Executes Dijkstra from Pacmans's target node as start 
    # to nearest pellet node as target.
    def getDijkstraPath(self, directions):
        lastPacmanNode = self.target
        lastPacmanNode = self.nodes.getVectorFromLUTNode(lastPacmanNode)
        pelletNode = self.findClosestPellet(self.nodes, lastPacmanNode, self.pelletLUT)
        #pelletNode = (1*TILEWIDTH, 4*TILEHEIGHT)

        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, lastPacmanNode, True, pelletNode)
        path = []
        node = pelletNode
        while node != lastPacmanNode:
            path.append(node)
            node = previous_nodes[node]
        path.append(lastPacmanNode)
        path.reverse()
        return path

    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath(directions)
        pacmanTarget = self.target
        pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
        nextPacmanTarget = path[1]
        self.debugPellet.position = Vector2(nextPacmanTarget[0], nextPacmanTarget[1])
        #print(len(path))
        if pacmanTarget[0] > nextPacmanTarget[0] and 2 in directions : #left
            print("LEFT")
            return 2
        if pacmanTarget[0] < nextPacmanTarget[0] and -2 in directions : #right
            print("RIGHT")
            return -2
        if pacmanTarget[1] > nextPacmanTarget[1] and 1 in directions : #up
            print("UP")
            return 1
        if pacmanTarget[1] < nextPacmanTarget[1] and -1 in directions : #down
            print("DOWN")
            return -1
        
        return self.direction
        # up 1, down -1, left 2, right -2

    def findClosestPellet(self, nodes, start_node, pelletLUT):
        queue = []
        queue.append(start_node)
        visited = copy.deepcopy(nodes.nodesLUT)
        for key in visited:
            visited[key] = False
        visited[start_node] = True

        while queue:
            node = queue.pop(0)
            neighbors = nodes.getNeighbors(node)

            for neighbor in neighbors:
                if visited[neighbor] == False:
                    queue.append(neighbor)
                    visited[neighbor] = True
                    if neighbor in pelletLUT:
                        return neighbor


        