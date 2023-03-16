import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from algorithms import dijkstra_or_a_star, dijkstra, a_star, Heuristic
from pellets import DebugPellet
import copy
import sys

class Pacman(Entity):
    def __init__(self, node, nodes, pelletLUT, pelletList, edges):
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
        self.pelletList = pelletList
        self.debugPellet = DebugPellet(10, 10)
        self.edges = edges
        self.goal = None
        self.tempDirection = LEFT
        self.ghosts = None
        self.debugPelletList = []
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
        
        if self.overshotTarget():
            #print(len(self.edges))
            if (self.node, self.target) in self.edges:
                e = self.edges.pop((self.node, self.target))
            elif (self.target, self.node) in self.edges:
                e = self.edges.pop((self.target, self.node))
            self.node = self.target
            directions = self.validDirections()
            self.tempDirection = self.directionMethod(directions)
            # ==========================================
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(self.tempDirection)
            if self.target is not self.node:
                self.direction = self.tempDirection
            else:
                self.target = self.getNewTarget(self.direction)
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(self.tempDirection):
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
        closestEdge = self.findClosestEdge(self.nodes, lastPacmanNode, self.edges)
        #closestEdge = self.findClosestEdgeBFS(self.nodes, lastPacmanNode)
        #closestEdge = self.findRandomEdge(self.nodes, lastPacmanNode, self.edges)

        #path = a_star(self.nodes, lastPacmanNode, closestEdge, Heuristic(closestEdge, self.ghosts))
        #return path

        self.debugPelletList = []
        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, lastPacmanNode, True, closestEdge, self.ghosts, self.debugPelletList)
        path = []
        #path.append(closestEdge.node2)
        node = closestEdge
        while node != lastPacmanNode:
            path.append(node)
            node = previous_nodes[node]
        path.reverse()
        return path

    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions):
        path = self.getDijkstraPath(directions)
        pacmanTarget = self.target
        pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
        nextPacmanTarget = path[0]
        ultimateTarget = path[len(path)-1]
        self.debugPellet.position = Vector2(ultimateTarget[0], ultimateTarget[1])
        if pacmanTarget[0] > nextPacmanTarget[0] and 2 in directions : #left
            #print("LEFT")
            return 2
        if pacmanTarget[0] < nextPacmanTarget[0] and -2 in directions : #right
            #print("RIGHT")
            return -2
        if pacmanTarget[1] > nextPacmanTarget[1] and 1 in directions : #up
            #print("UP")
            return 1
        if pacmanTarget[1] < nextPacmanTarget[1] and -1 in directions : #down
            #print("DOWN")
            return -1
        
        return self.direction
        # up 1, down -1, left 2, right -2

    def findClosestEdgeBFS(self, nodes, start_node):
        queue = []
        queue.append(start_node)
        visited = copy.deepcopy(nodes.nodesLUT)
        for key in visited:
            visited[key] = False
        visited[start_node] = True
        edgeNode1Dict = {}
        for key in self.edges:
            edgeNode1Dict[self.edges[key].node1] = self.edges[key]

        while queue:
            node = queue.pop(0)
            neighbors = nodes.getNeighbors(node)

            for neighbor in neighbors:
                if visited[neighbor] == False:
                    queue.append(neighbor)
                    visited[neighbor] = True
                    if neighbor in edgeNode1Dict:
                        return edgeNode1Dict[neighbor]
                    
    def findClosestEdge(self, nodes, start_node, edges):
        minDist = sys.maxsize
        closestEdge = None
        for key in edges:
            edge = edges[key]
            node1Vec = Vector2(edge.node1[0], edge.node1[1])
            node2Vec = Vector2(edge.node2[0], edge.node2[1])
            skipEdge = False
            for ghost in self.ghosts:
                targetNeighbor = ghost.target.neighbors[ghost.direction]
                if ghost.target.position == node1Vec or ghost.target.position == node2Vec or ghost.node.position == node1Vec or ghost.node.position == node2Vec:
                    skipEdge = True
                elif targetNeighbor is not None:
                    if targetNeighbor.position == node1Vec or targetNeighbor.position == node2Vec or targetNeighbor.position == node1Vec or targetNeighbor.position == node2Vec:
                        skipEdge = True
            if not skipEdge:
                if edge.node1 != start_node:
                    vec = Vector2(edge.node1[0], edge.node1[1]) - Vector2(start_node[0], start_node[1])
                    vecLength = vec.magnitudeSquared()
                    if vecLength < minDist:
                        minDist = vecLength
                        closestEdge = edges[key].node1
                else:
                    closestEdge = edge.node2
                    break
            else:
                skipEdge = False
        if closestEdge is None:
            closestEdge = self.findRandomEdge(nodes, start_node, edges)
        return closestEdge  
    
    def findRandomEdge(self, nodes, start_node, edges):
        minDist = sys.maxsize
        closestEdge = None
        edgesByDistance = {}
        for key in edges:
            edge = edges[key]
            if edge.node1 != start_node:
                vec = Vector2(edge.node1[0], edge.node1[1]) - Vector2(start_node[0], start_node[1])
                vecLength = vec.magnitudeSquared()
                edgesByDistance[vecLength] = edges[key]

        lengths = list(edgesByDistance.keys())
        lengths.sort()
        closestEdge = edgesByDistance[lengths[len(lengths)-1]]
        return closestEdge.node1