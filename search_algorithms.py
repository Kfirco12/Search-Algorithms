
#Variable defenitions
UP="U"
DOWN="D"
RIGHT="R"
LEFT="L"
IDS=1
BFS=2
A_STAR=3
board_size = -1
init_state = []
working_algorithm=-1
solution=[]


#===========================================================
#======================= Algorithms ========================
#IDS algorithm - devided to 2 part. One is a DFS above and the this part is running DFS with iterated limits.
def ids():
    queue = [init_state] #implemented as stack
    route = [] # represents the final rout to the solution
    vertex_num = 0 #count the states we inserted to the open-list.

    limit= 0
    while True: # increase the limit every iteration until a solution is found.
        found,route,vertex_num = dfs(queue[:],limit,route[:],1) #zero the queue and the rout at every iteration.
        if found:
            break
        else:
            limit+=1
    return route,vertex_num,limit

#simple DFS limited to the variable depth. Returns the route if the solution found with boolean idicator.
# Retuns False as indicator and empty route if the solution is not found in the current running.
def dfs(queue,depth,route,vertex_num):
    if depth == 0:
        return False, route, vertex_num
    if queue[-1] == solution:
        return True, route, vertex_num
    row, col, blank,directions = get_directions(queue[-1]) # get the possible sons of the current state.
    for direct in directions:
        route.append(direct)
        found,_ = set_cube(direct,row,col,queue[-1],queue,blank) #set the posible moves and insert the sons to the the queue
        vertex_num+=1
        if found:
            return True, route,vertex_num
        found,_,vertex_num = dfs(queue, depth - 1, route, vertex_num)
        if found:
            return True, route, vertex_num
        else:
            del route[-1]
            del queue[-1]
    return False, [], vertex_num # false if not found and an emty route for the solution.
# -----------------------------------------------------------

#BFS alg. enter the new state to the queue by the defined order. stop if we got the final solution.
def bfs():
    STATE_INDEX=0
    queue,state, vertex_num = [],init_state, 1 # initial states of the algorithm
    father_num, last_key = -1,0 # father for retriving the route, and last key for updating dictionary data structure.
    route = {str(last_key):[state,father_num,""]} #here route is the data structure(as a dictionary) and will give us the route by the ancient fathers.
    queue.append(route)
    while len(queue)!=0:
        data=queue.pop(0) #FIFO list.
        father_num,value = list(data.keys())[0],list(data.values())[0] #first in the queue
        state=value[STATE_INDEX]
        row,col,blank,directions = get_directions(state)
        found,tmp_dict = set_cube(directions,row,col,state,[],blank,father_num,last_key) #set the posible moves and insert the sons to tmp dictionary.
        route.update(tmp_dict)
        vertex_num+=len(tmp_dict.keys())
        last_key=int(list(route.keys())[-1]) #for updating the new key.
        for key, value in tmp_dict.items():
            queue.append({key:value})
        if found:
            break #break if we found the solution
    str_route=get_final_route(route)
    return str_route,vertex_num,0
# -----------------------------------------------------------

def a_star():
    STATE_INDEX, FATHER_INDEX, DIRECTION, PAST_COST_INDEX, F_INDEX = 0, 1, 2, 3, 4 # constants for the dictionary data strucure
    queue, state, vertex_num = [], init_state, 1 # initial states of the algorithm
    father_num, last_key = -1, 0 # father for retriving the route, and last key for updating dictionary data structure.
    route = {str(last_key): [state, father_num, "",0,0]}
    queue.append(route)
    while len(queue)!=0:
        data=queue.pop(0) # top of the queue
        vertex_num+=1
        father_num,value = list(data.keys())[0],list(data.values())[0] #first in the queue
        state=value[STATE_INDEX]
        row,col,blank,directions = get_directions(state)
        found,tmp_dict = set_cube(directions,row,col,state,[],blank,father_num,last_key,value[PAST_COST_INDEX]+1) #set the posible moves and insert the sons to tmp dictionary.
        set_cost(tmp_dict,STATE_INDEX,PAST_COST_INDEX,F_INDEX) #set the cost of each son
        route.update(tmp_dict)
        if found:
            break #break if we found the solution
        for key, value in tmp_dict.items():
            queue.append({key:value}) # add the new states to the queue
        last_key=int(list(route.keys())[-1]) #for updating the new key.
        queue=prioritize(queue[:],F_INDEX) # sort the queue by the cost of the states.
    str_route = get_final_route(route)
    depth=list(route.values())[-1][PAST_COST_INDEX]
    return str_route, vertex_num, depth

#===========================================================
#=================== Helping Methods =======================
# -----------------------------------------------------------
# decides which algorithm should work and print the solution.
def search():
    if working_algorithm == IDS:
        route, vertex_num, depth=ids()
    elif working_algorithm == BFS:
        route, vertex_num, depth=bfs()
    elif working_algorithm == A_STAR:
        route, vertex_num, depth=a_star()
    print_to_file(route,vertex_num,depth)

# -----------------------------------------------------------
# gets an array of directions and return the direction as a string.
def get_final_route(route_arr):
    FATHER_INDEX, DIRECTION = 1, 2
    goal_key = list(route_arr.keys())[-1]  # the last value in the queue is the solution.
    str_route = ""
    # start from the solution and find the ancient fathers.
    while goal_key != '0':
        cur_node=list(route_arr.values())[int(goal_key)]
        str_route+=cur_node[DIRECTION]
        goal_key=cur_node[FATHER_INDEX]
    return str_route[::-1]

# -----------------------------------------------------------
# print the route of the correct solution, number of opened vertexes and solution depth to a file.
def print_to_file(route,vertex_num,depth):
    new_route = ""
    for str in route:
        new_route+=str
    f = open("output.txt", "w+")
    f.write('{0} {1} {2}'.format(new_route,vertex_num,depth))
    f.close()

# -----------------------------------------------------------
#return the blank place, his row, his collumn and the possible direction (sons) of the current cube state.
def get_directions(state):
    blank = find_blank(state)
    row = blank // board_size
    col = blank % board_size
    directions=[]
    if row < board_size - 1: # UP
        directions.append(UP)
    if row > 0: # DOWN
        directions.append(DOWN)
    if col < board_size - 1:  # LEFT
        directions.append(LEFT)
    if col > 0:  # RIGHT
        directions.append(RIGHT)
    return row,col,blank,directions

# -----------------------------------------------------------
#create the sons of the current state. return the new route and if the solution was found.
def set_cube(directions,row,col,state,queue,blank,father_num=-1,my_num=-1,depth=0):
    found_solution=True
    dict={}
    my_num+=1
    if UP in directions: # UP
        new_state = swap(state, board_size * (row + 1) + col, blank)
        queue.append(new_state)
        my_num=set_dict(my_num,[new_state,father_num,UP], dict,depth) # saves the sate in a dictionary.
        if new_state == solution:
            return found_solution, dict
    if DOWN in directions:  # DOWN
        new_state = swap(state, board_size * (row - 1) + col, blank)
        queue.append(new_state)
        my_num = set_dict(my_num, [new_state, father_num, DOWN], dict,depth)
        if new_state == solution:
            return found_solution,dict
    if LEFT in directions:  # LEFT
        new_state = swap(state, board_size * row + (col + 1), blank)
        queue.append(new_state)
        my_num = set_dict(my_num, [new_state, father_num, LEFT], dict,depth)
        if new_state == solution:
            return found_solution,dict
    if RIGHT in directions:  # RIGHT
        new_state = swap(state, board_size * row + (col - 1), blank)
        queue.append(new_state)
        my_num = set_dict(my_num, [new_state, father_num, RIGHT], dict,depth)
        if new_state == solution:
            return found_solution,dict
    return not found_solution,dict

# -----------------------------------------------------------
# gets an enrolled number(key), and parameters and update a dictionary.
def set_dict(my_num, values, dict,depth):
    tmp_dict={}
    if working_algorithm==A_STAR:
        tmp_dict = {str(my_num): [values[0], values[1], values[2],depth,0]}
    else:
        tmp_dict = {str(my_num): [values[0], values[1], values[2]]}
    dict.update(tmp_dict)
    my_num += 1
    return my_num

# -----------------------------------------------------------
# swaping between the blank slot to a different slot in a state.
def swap(state, to_swap, blank):
    tmp_state = state[:]
    tmp = state[to_swap]
    tmp_state[to_swap] = 0
    tmp_state[blank] = tmp
    return tmp_state

# -----------------------------------------------------------
# find the blank slot. assuming there is an empty slot.
def find_blank(state):
    for i in range(0,len(state)):
        if state[i]==0:
            return i

 # -----------------------------------------------------------
# set the cost of a state by the number of move it had + the huristic function.
def set_cost(dict, state_index,past_cost,f_index):
    for key, value in dict.items():
        g=value[past_cost]
        h=manhattan_distance(value[state_index])
        value[f_index] = g+h

# -----------------------------------------------------------
# the chosen huristic function. gets a state and sum the moves any slot needs to do for the correct state.
def manhattan_distance(state):
    distance=0
    for i in range(0,len(state)):
        if state[i]!= 0:
            x=i//board_size - (state[i]-1)//board_size
            y=i%board_size - ((state[i]-1)%board_size)
            distance+=(abs(x)+abs(y))
    return distance

# -----------------------------------------------------------
#sort dictionary of states by the costs of the slots.
def prioritize(queue,f_index):
    priority_queue=[]
    tmp_dict={}
    for x in queue:
        line={list(x.keys())[0]:list(x.values())[0]}
        tmp_dict.update(line)
    for key, value in sorted(tmp_dict.items(), key=lambda v: v[1][f_index]): #sort the dictionary - O(nlogn)
        priority_queue.append({key:value}) # update the new order of the queue by state's cost.
    return priority_queue

# ===========================================================
# handle the input - saves the relevant parameters and validate the input file context.
def getInput():
    global working_algorithm
    global board_size
    global blank_place
    # Read the file and initialize the relevant variables.
    try:
        with open("input.txt", "r") as f:
            lines = f.readlines()
        f.close()
    except:
        print("Failed to read 'input.txt' file!")
        return False

    # Initialize variables.
    if lines.__len__() < 3:
        print("Invalid parameters!")
        return False
    #saving input as integers for convenience
    try:
        working_algorithm = int(lines[0]);
        board_size = int(lines[1])
        #initialize solution vector.
        for i in range (0,(board_size*board_size)-1):
            solution.append(i+1)
        solution.append(0)
        #convert input graph to integers.
        tmp_board_path = lines[2].split("-")
        for str in tmp_board_path:
            init_state.append(int(str))
        if len(init_state) != board_size*board_size:
            print("Invalid parameters!")
            return False
    except:
        print("Invalid parameters!")
        return False
    return True

# ===========================================================
#main. running the input check method and runing the search if the input is correct.
if '__main__' == __name__:
    if getInput():
        search()
    else:
        print("A problem accured with getting the input file content")