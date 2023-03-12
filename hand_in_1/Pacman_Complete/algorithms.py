import sys

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
