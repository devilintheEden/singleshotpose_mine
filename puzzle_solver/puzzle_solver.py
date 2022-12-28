import networkx as nx
import sys
import copy

'''
is_relative: is position relative to block
position: relative position inside block / global position on board (vertical as first element, horizontal as second element)
direction: ("w","e")
level: floor level
'''
class Corridor:
    def __init__(self, is_relative, position, direction, level):
        self.is_relative = is_relative
        self.position = position
        self.direction = direction
        self.level = level

    def border_level(self):
        #(north, east, south, west)
        temp = [-1,-1,-1,-1]
        if("n" in self.direction):
            temp[0] = self.level
        if("e" in self.direction):
            temp[1] = self.level
        if("s" in self.direction):
            temp[2] = self.level
        if("w" in self.direction):
            temp[3] = self.level
        return tuple(temp)
    
    def to_string(self):
        return "Corridor: " + str(self.is_relative) + " " + str(self.position) + " " + self.direction + " " + str(self.level)

'''
direction: the direction of the higher side ("e"/"w"/"n"/"s")
level: the floor level of the higher side
'''
class Stair:
    def __init__(self, is_relative, position, direction, level):
        self.is_relative = is_relative
        self.position = position
        self.direction = direction
        self.level = level
    
    def border_level(self):
        #(north, east, south, west)
        if(self.direction == "n"):
            return (self.level, -1, self.level - 1, -1)
        elif(self.direction == "s"):
            return (self.level - 1, -1, self.level, -1)
        elif(self.direction == "e"):
            return (-1, self.level, -1, self.level - 1)
        else:
            return (-1, self.level - 1, -1, self.level)

    def to_string(self):
        return "Stair: " + str(self.is_relative) + " " + str(self.position) + " " + self.direction + " " + str(self.level)

class Platform:
    def __init__(self, is_relative, position, level):
        self.is_relative = is_relative
        self.position = position
        self.level = level

    def border_level(self):
        #(north, east, south, west)
        return (self.level, self.level, self.level, self.level)

    def to_string(self):
        return "Platform: " + str(self.is_relative) + " " + str(self.position) + " " + str(self.level)

'''
position: the global position of platform 1
direction: the direction of the side with platforms 1,2 ("e"/"w"/"n"/"s")
platforms: an array containing all platforms in block
'''
class Block:
    def __init__(self, position, direction, platforms):
        self.position = position
        self.direction = direction
        self.platforms = platforms

    def local_pos_to_global(self, local_pos):
        if(self.direction == "n"):    
            return (local_pos[0] + self.position[0], local_pos[1] + self.position[1])
        if(self.direction == "s"):
            return (self.position[0] - local_pos[0], self.position[1] - local_pos[1])
        if(self.direction == "e"):
            return (self.position[0] + local_pos[1], self.position[1] - local_pos[0])
        if(self.direction == "w"):
            return (self.position[0] - local_pos[1], self.position[1] + local_pos[0])

    def local_dir_to_global_helper(self, local_dir):
        if(self.direction == "n"):
            return local_dir
        if(self.direction == "s"):
            dictionary = {"n": "s", "s": "n", "e": "w", "w": "e"}
            return dictionary[local_dir]
        if(self.direction == "e"):
            dictionary = {"n": "e", "s": "w", "e": "s", "w": "n"}
            return dictionary[local_dir]
        if(self.direction == "w"):
            dictionary = {"n": "w", "s": "e", "e": "n", "w": "s"}
            return dictionary[local_dir]

    def local_dir_to_global(self, local_dir):
        if(type(local_dir) is tuple):
            return (self.local_dir_to_global_helper(local_dir[0]), self.local_dir_to_global_helper(local_dir[1]))
        else:
            return self.local_dir_to_global_helper(local_dir)

    def place_block_in(self, block_pos, block_dir):
        self.position = block_pos
        self.direction = block_dir
        result = copy.copy(self.platforms)
        for i in range(len(result)):
            result[i].is_relative = False
            result[i].position = self.local_pos_to_global(result[i].position)
            if type(result[i]) != Platform:
                result[i].direction = self.local_dir_to_global(result[i].direction)
        return result

def place_block_tower(tower_pos, tower_dir):
    return fixed_initial_platforms + block_tower.place_block_in(tower_pos, tower_dir)

def place_moving_blocks(block, block_pos, block_dir):
    return block.place_block_in(block_pos, block_dir)

def define_current_puzzle_status(fixed_puzzle_platforms, moving_blocks_list):
    current_puzzle_platforms = fixed_puzzle_platforms
    grid_map = [[[] for x in range(7)] for y in range(7)]
    for i in range(len(moving_blocks_list)):
        current_puzzle_platforms = current_puzzle_platforms + place_moving_blocks(*moving_blocks_list[i])
    for i in range(len(current_puzzle_platforms)):
        temp_pos = current_puzzle_platforms[i].position
        grid_map[temp_pos[0]][temp_pos[1]].append(i)
    for i in range(7):
        for j in range(7):
            if(len(grid_map[i][j]) == 0 and not(i == 0 and j == 0) and not(i == 0 and j == 6)):
                current_puzzle_platforms.append(Platform(False, (i,j), 0))
                grid_map[i][j].append(len(current_puzzle_platforms) - 1)
    return grid_map, current_puzzle_platforms

def get_current_network(grid_map, current_puzzle_platforms):
    G = nx.Graph()
    for i in range(len(current_puzzle_platforms)):
        this_platform = current_puzzle_platforms[i]
        coor = this_platform.position
        # up
        if(coor[0] > 0):
            for k in grid_map[coor[0] - 1][coor[1]]:
                if(k > i):
                    another_platform = current_puzzle_platforms[k]
                    if(this_platform.border_level()[0] == another_platform.border_level()[2]):
                        G.add_edge(i,k)
        # down
        if(coor[0] < 6):
            for k in grid_map[coor[0] + 1][coor[1]]:
                if(k > i):
                    another_platform = current_puzzle_platforms[k]
                    if(this_platform.border_level()[2] == another_platform.border_level()[0]):
                        G.add_edge(i,k)
        # left
        if(coor[1] > 0):
            for k in grid_map[coor[0]][coor[1] - 1]:
                if(k > i):
                    another_platform = current_puzzle_platforms[k]
                    if(this_platform.border_level()[3] == another_platform.border_level()[1]):
                        G.add_edge(i,k)
        # right
        if(coor[1] < 6):
            for k in grid_map[coor[0]][coor[1] + 1]:
                if(k > i):
                    another_platform = current_puzzle_platforms[k]
                    if(this_platform.border_level()[1] == another_platform.border_level()[3]):
                        G.add_edge(i,k)
    return G

def write_Txt_File(file_path, content):
    f = open(file_path, "w+")
    f.write(content)

block_A = Block((0,0), "n", [Platform(True, (0,0), 1), Platform(True, (0,1), 2), Corridor(True, (0,1), ("w", "e"), 1), Platform(True, (1,0), 1), Platform(True, (1,1), 1), Stair(True, (2,0), "e", 1), Corridor(True, (2,1), ("w", "e"), 0)])
block_B = Block((0,0), "n", [Platform(True, (0,0), 2), Platform(True, (0,1), 2), Platform(True, (1,0), 2), Platform(True, (1,1), 1), Platform(True, (2,0), 1), Stair(True, (2,1), "n", 1)])
block_C = Block((0,0), "n", [Platform(True, (0,0), 1), Platform(True, (0,1), 1), Platform(True, (1,0), 2), Platform(True, (1,1), 1), Platform(True, (2,0), 2), Stair(True, (2,1), "w", 2)])
block_D = Block((0,0), "n", [Platform(True, (0,0), 1), Stair(True, (0,1), "s", 2), Stair(True, (0,2), "n", 1), Platform(True, (1,0), 1), Platform(True, (1,1), 2), Corridor(True, (1,2), ("n", "e"), 0)])
block_E = Block((0,0), "n", [Platform(True, (0,0), 2), Platform(True, (0,1), 1), Stair(True, (1,0), "e", 1), Platform(True, (1,1), 1), Platform(True, (2,0), 1), Stair(True, (2,1), "s", 2)])
block_tower = Block((0,0), "n", [Platform(True, (0,0), 2), Corridor(True, (0,0), ("w", "e"), 1), Platform(True, (0,1), 1), Stair(True, (1,0), "s", 3), Platform(True, (1,1), 3), Platform(True, (2,0), 3), Platform(True, (2,1), 3)])
fixed_initial_platforms = [Platform(False, (5,6), 1), Stair(False, (6,6), "n", 1)]
start_point_index = 6
finish_point_index = 1

if __name__ == "__main__":
    blocks_in_order = [block_A, block_B, block_C, block_D, block_E]
    file_path = "puzzle_result.txt"
    fixed_puzzle_platforms = []
    parameters = sys.argv[1:]
    movable_blocks = []
    for i in range(6):
        y = int(parameters[3 * i])
        x = int(parameters[3 * i + 1])
        if(x >= 0 and x <= 6 and y >= 0 and y <= 6):
            if(i == 5):
                fixed_puzzle_platforms = place_block_tower((x,y), parameters[3 * i + 2])
            else:
                movable_blocks.append([blocks_in_order[i], (x,y), parameters[3 * i + 2]])
    grid_map, current_puzzle_platforms = define_current_puzzle_status(fixed_puzzle_platforms, movable_blocks)
    G = get_current_network(grid_map, current_puzzle_platforms)
    try:
        if(nx.has_path(G, start_point_index, finish_point_index)):
            temp = nx.shortest_path(G, source=start_point_index, target=finish_point_index)
            result = ""
            for i in temp:
                result += str(current_puzzle_platforms[i].position[0]) + " " + str(current_puzzle_platforms[i].position[1]) + " " + str(current_puzzle_platforms[i].level) + " "
            result = result[:-1]
            write_Txt_File(file_path, result)
        else:
            write_Txt_File(file_path, "false")
    except nx.NodeNotFound:
        write_Txt_File(file_path, "false")
