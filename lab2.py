import sys
import enum
import heapq
import psutil
import os

TREE = None 
H1_H2 = False

class Tree:
    __nodes = []
    __hashes = {}
    def add_node(self, new_node: "Node"):
        if (not self.hasState(new_node.current_state)):
            self.__nodes.append(new_node)
            self.__hashes[state_hash(new_node.current_state)] = new_node

    def getNode(self, node: int) -> list["Node"]:
        return list(self.__nodes[node])

    def getNodeByState(self, state: list) -> "Node":
        return self.__hashes[state_hash(state)]
    
    def hasState(self, state: list) -> bool:
        return state_hash(state) in self.__hashes

    def print_node(self, node: "Node"):
        node_prev_action: str = None
        if(node.previous_action):
            node_prev_action = node.previous_action.name
        print(f"action = {node_prev_action}, " +
            f"count = {node.path_cost}")
        self.print_state(node.current_state)
        print("")

    def print_state(self, state: list):
        for i in range(9):
            if (i % 3 == 0 and i != 0):
                 print("")
            print(state[i] if state[i] != 0 else " ", end=" ")

    def print_path(self, node: "Node", isReversed = False):
        path = []
        current_node = node

        while current_node.parent_node:
            path.append(current_node)
            current_node = current_node.parent_node
        path.append(current_node)
        if (isReversed):
            path = path[::-1]
        for path_node in path:
            self.print_node(path_node)


class Action(enum.Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4

class Node:
    current_state: list = None
    parent_node: "Node" = None
    previous_action: Action = None
    path_cost: int = 0
    node_id: int = 0
    nodes_count = 0

    def __init__(self, state: list, parent: "Node", action: Action, cost: int):
        self.current_state = state
        self.parent_node = parent
        self.previous_action = action
        self.path_cost = cost
        self.node_id = Node.nodes_count
        Node.nodes_count += 1

    @classmethod
    def get_nodes_count(cls) -> int:
        return cls.nodes_count + 1

def get_initial_state() -> list:
    return [5, 8, 3,
            4, 0, 2,
            7, 6, 1 ]

def get_finish_state() -> list:
    return [1, 2, 3,
            4, 5, 6,
            7, 8, 0 ]


def check_final(current_state: list) -> bool:
    return current_state == get_finish_state()


def state_hash(state: list) -> int:
    hash = 7
    for i in state:
        hash = 31*hash + i
    return hash


def heuristics(node: "Node") -> int:
    if(not H1_H2):
        cur_value = node.path_cost + h1(node.current_state)
    else:
        cur_value = node.path_cost + h2(node.current_state)
    return cur_value


def h1(state: list) -> int:
    state_final = get_finish_state()
    res = 0
    for i in range(9):
        if(state_final[i] != state[i]):
            res+=1
    return res

def h2(state: list) -> int:
    state_final = get_finish_state()
    res = 0
    for i in range(9):
        state_x, state_y = i // 3, i % 3
        where = state_final.index(state[i])
        final_x, final_y = where // 3, where % 3
        res += abs(final_x-state_x) + abs(final_y-state_y)
    return res

def print_info(iterations: int):
    print(f"Итого узлов: {Node.get_nodes_count()}")
    print(f"Итого итераций: {iterations}")
    print(f"Памяти использовано: {psutil.Process(os.getpid()).memory_info().rss} байтов")

def state_swap(new_states: dict, current_state: list, i: int, j: int, action: Action):
    state = list(current_state)
    state[i], state[j] = state[j], state[i]
    new_states[action] = state

def get_new_states(current_state: list) -> dict[Action, list[Node]]:
    new_states = {}
    pos = current_state.index(0)
    if pos not in (0, 1, 2):
        state_swap(new_states, current_state, pos, pos-3, Action.UP)
    if pos not in (6, 7, 8):
        state_swap(new_states, current_state, pos, pos+3, Action.DOWN)
    if pos not in (2, 5, 8):
        state_swap(new_states, current_state, pos, pos+1, Action.RIGHT)
    if pos not in (0, 3, 6):
        state_swap(new_states, current_state, pos, pos-1, Action.LEFT)
    return new_states

def get_neighbours(node: Node) -> list[Node]:
    new_states_dict = get_new_states(node.current_state)
    neighbours = []
    for new_state_action in new_states_dict:
        new_state = new_states_dict[new_state_action]
        if (TREE.hasState(new_state)):
            neighbours.append(TREE.getNodeByState(new_state))
        else:
            new_node = Node(new_state, node, new_state_action, node.path_cost+1)
            neighbours.append(new_node)
            TREE.add_node(new_node)
    return neighbours

def A_star():
    open_list = set()
    close_list = set()
    heap = []
    Found = False

    current_node = Node(get_initial_state(), None, None, 0)
    TREE.add_node(current_node)
    close_list.add(current_node)
    neighbours = get_neighbours(current_node)
    for neighbour in neighbours:
        open_list.add(neighbour.node_id)
        neighbour_h = heuristics(neighbour)
        heapq.heappush(heap, (neighbour_h, neighbour.node_id, neighbour))
    iteration_count = 0
    step_i = 0

    while(not Found):
        iteration_count+=1
        heap_lowest = heapq.heappop(heap)
        current_node: Node = heap_lowest[2]
        open_list.remove(current_node.node_id)
        close_list.add(current_node.node_id)
        if (check_final(current_node.current_state)):
            Found = True
            TREE.print_path(current_node)
            print_info(iteration_count)
            break
        neighbours = get_neighbours(current_node)
        for neighbour in neighbours:
            if (neighbour.node_id in open_list):
                old_g = neighbour.path_cost
                new_g = current_node.path_cost + 1
                if (new_g < old_g):
                    neighbour.path_cost = new_g
                    neighbour.parent_node = current_node
            else:
                if(neighbour.node_id not in close_list):
                    open_list.add(neighbour.node_id)
                    neighbor_i_h = heuristics(neighbour)
                    heapq.heappush(heap, (neighbor_i_h, neighbour.node_id, neighbour))
        step_i += 1

if __name__ == '__main__':
    TREE = Tree()
    A_star()