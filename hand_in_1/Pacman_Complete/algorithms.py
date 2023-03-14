import sys
from vector import Vector2

class NodeRecord():
    def __init__(self):
        self.node = None
        self.connection = None
        self.costSoFar = None
        self.estimatedTotalCost = None

class Connection():
    def __init__(self, cost, fromNode, toNode):
        self.cost = self.calculateCost(fromNode, toNode)
        self.fromNode = fromNode
        self.toNode = toNode

    def getCost(self):
        return self.cost
    
    def getFromNode(self):
        return self.fromNode
    
    def getToNode(self):
        return self.toNode
    
    def calculateCost(self, fromNode, toNode):
        connectionLength = Vector2(fromNode[0], fromNode[1]) - Vector2(toNode[0], toNode[1])
        return connectionLength.magnitudeSquared()
    
class Heuristic():
    def __init__(self, goalNode, ghosts):
        self.goalNode = goalNode
        self.ghosts = ghosts

    def estimate(self, fromNode):
        #heuristic = 512*512
        #for ghost in self.ghosts:
        #    connection = Vector2(fromNode[0], fromNode[1]) - ghost.position
        #    heuristic -= connection.magnitudeSquared()
        value = heuristic(fromNode, self.goalNode)
        print(value)
        return value

class PathfindingList():
    def __init__(self):
        self.list = []

    def add(self, nodeRecord):
        self.list.append(nodeRecord)

    def remove(self, nodeRecord):
        self.list.remove(nodeRecord)

    def smallestElement(self):
        smallestCost = sys.maxsize
        smallestElement = None
        for element in self.list:
            if element.estimatedTotalCost < smallestCost:
                smallestElement = element
        return smallestElement
    
    def length(self):
        return len(self.list)
    
    def contains(self, node):
        for element in self.list:
            if element.node is node:
                return True
        return False

    def find(self, node):
        for element in self.list:
            if element.node is node:
                return element
        return None


def a_star(nodes, startNode, endNode, heuristic):
    # Initialize the record for the start node.
    startRecord = NodeRecord()
    startRecord.node = startNode
    startRecord.connection = None
    startRecord.costSoFar = 0
    startRecord.estimatedTotalCost = heuristic.estimate(startNode)

    # Initialize the open and closed lists.
    open = PathfindingList()
    open.add(startRecord)
    closed = PathfindingList()
    current = None

    while open.length() > 0:
        # Find the smallest element in the open list (using the
        # estimatedTotalCost).
        current = open.smallestElement()

        # If it is the goal node, then terminate.
        if current.node == endNode:
            break

        # Otherwise get its outgoing connections.
        neighbors = nodes.getNeighbors(current.node)

        # Loop through each connection in turn.
        for neighbor in neighbors:
            connection = Connection(0, current.node, neighbor)

            connectionEnd = connection.getToNode()
            connectionEndCost = current.costSoFar + connection.getCost()

            # If the node is closed we may have to skip, or remove it
            # from the closed list.
            if closed.contains(connectionEnd):
                # Here we find the record in the closed list
                # corresponding to the endNode.
                connectionEndRecord = closed.find(connectionEnd)

                # If we didn’t find a shorter route, skip.
                if connectionEndRecord.costSoFar <= connectionEndCost:
                    continue

                # Otherwise remove it from the closed list.
                closed.remove(connectionEndRecord)

                # We can use the node’s old cost values to calculate
                # its heuristic without calling the possibly expensive
                # heuristic function.
                connectionEndHeuristic = connectionEndRecord.estimatedTotalCost - connectionEndRecord.costSoFar

            # Skip if the node is open and we’ve not found a better
            # route.
            elif open.contains(connectionEnd):
                # Here we find the record in the open list
                # corresponding to the endNode.
                connectionEndRecord = open.find(connectionEnd)

                # If our route is no better, then skip.
                if connectionEndRecord.costSoFar <= connectionEndCost:
                    continue

                # Again, we can calculate its heuristic.
                connectionEndHeuristic = connectionEndRecord.estimatedTotalCost - connectionEndRecord.costSoFar

            # Otherwise we know we’ve got an unvisited node, so make a
            # record for it.
            else:
                connectionEndRecord = NodeRecord()
                connectionEndRecord.node = connectionEnd

                # We’ll need to calculate the heuristic value using
                # the function, since we don’t have an existing record
                # to use.
                connectionEndHeuristic = heuristic.estimate(connectionEnd)

            # We’re here if we need to update the node. Update the
            # cost, estimate and connection.
            connectionEndRecord.costSoFar = connectionEndCost
            connectionEndRecord.estimatedTotalCost = connectionEndCost + connectionEndHeuristic
            connection.fromNode = current
            connection.toNode = connectionEndRecord
            connectionEndRecord.connection = connection

            # And add it to the open list.
            if not open.contains(connectionEnd):
                open.add(connectionEndRecord)

        # We’ve finished looking at the connections for the current
        # node, so add it to the closed list and remove it from the
        # open list.
        open.remove(current)
        closed.add(current)

    # We’re here if we’ve either found the goal, or if we’ve no more
    # nodes to search, find which.
    if current.node != endNode:
        # We’ve run out of nodes without finding the goal, so there’s
        # no solution.
        return None
    
    else:
        # Compile the list of connections in the path.
        path = []
        
        # Work back along the path, accumulating connections.
        while current.node != startNode:
            path.append(current.connection.toNode.node)
            current = current.connection.getFromNode()

        # Reverse the path, and return it.
        path.reverse()
        return path





def dijkstra(nodes, start_node):
    unvisited_nodes = list(nodes.costs)
    #print(unvisited_nodes[0])
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbors = nodes.getNeighbors(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + 1 #nodes.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node
 
        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    
    return previous_nodes, shortest_path

def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    # Add the start node manually
    path.append(start_node)
    
    print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
    #print(path)


#########
# A*
def heuristic(node1, node2):
    # manhattan distance
    return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])


def dijkstra_or_a_star(nodes, start_node, a_star, goal):
    # list of all nodes
    unvisited_nodes = list(nodes.costs)
    # dict with {"node"-"value of costSoFar + costOfBestEdges"} as key-value pair 
    shortest_path = {}
    # dict with {"node"-"best previous node to get to this node"} as key-value pair 
    previous_nodes = {}
    # dict with {"node"-"value of costSoFar + costOfBestEdges + heuristic"} as key-value pair
    totalEstimatedCost = {}

    # initialise all the nodes 
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
        totalEstimatedCost[node] = max_value
    # initialise starting node
    shortest_path[start_node] = 0
    totalEstimatedCost[start_node] = heuristic(start_node, goal)

    # while there are still unvisited nodes:
    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            # base case
            if current_min_node == None:
                current_min_node = node
            # if we found the goal node, look no further 
            elif node == goal:
                current_min_node = node
                break
            # if alg. is A*, use the heuristic (totalEstimatedCost) to choose next best node...
            elif a_star and (totalEstimatedCost[node] < totalEstimatedCost[current_min_node]):
                current_min_node = node
            # ...otherwise use the normal cost value to choose the next best node.
            elif not a_star and (shortest_path[node] < shortest_path[current_min_node]):
                current_min_node = node

        
        neighbors = nodes.getNeighbors(current_min_node)
        for neighbor in neighbors:
            if neighbor in shortest_path:
                # tentative value only considers costSoFar + edgeCost
                tentative_value = shortest_path[current_min_node] + 1
                # if this value is better than what we found so far...
                if tentative_value < shortest_path[neighbor]:
                    # ...store it, without the heuristic (to avoid accumulation).
                    shortest_path[neighbor] = tentative_value
                    # We also update the best path to the current node
                    previous_nodes[neighbor] = current_min_node
                    # dont forget to update the heuristic dictionary if we are using A*
                    if a_star:
                        totalEstimatedCost[neighbor] = tentative_value + heuristic(neighbor, goal)
 
        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    return previous_nodes, shortest_path
