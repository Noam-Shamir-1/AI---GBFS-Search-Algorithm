import copy

import search
import random
import math
from itertools import product
import ast


ids = ["316299098", "316508126"]



class DroneProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.turn = -1
        self.t = 0
        self.map = initial["map"]
        initial_state = {
            "drones": {k: [v, 'empty', 'empty'] for (k, v) in initial["drones"].items()},
            "packages": {k: [v, 'floor'] for (k, v) in initial["packages"].items()},
            "clients": {k: {"path": v["path"], "packages": v["packages"],"position_index": 0, "recieved": []} for (k, v) in
                        initial["clients"].items()},
            "recieved": []
        }
        self.N = len(self.map)
        self.M = len(self.map[0])
        self.relevant_pakages = self.relevant_pak(initial_state)
        self.move_score = self.make_move_grid(initial)

        self.total_wanted_packages = 0
        for v in initial_state["clients"].values():
            self.total_wanted_packages += len(v["packages"])

        self.package_rank = self.package_rank(initial_state)
        self.package_match = self.package_matching(initial_state)
        self.pick_flag = self.relevant_pak(initial_state)
        initial_state = self.dic_to_string(initial_state)
        search.Problem.__init__(self, initial_state)

    def package_matching(self, initial_state):
        dict = {k: 0 for k in initial_state["packages"].keys()}
        for man in initial_state["clients"]:
            for p in initial_state["clients"][man]["packages"]:
                dict[p] = man
        return dict

    def package_rank(self, initial_state):
        #return: for each drone: 1 + distance from his client
        dict = {k:1 for k in initial_state["packages"].keys()}
        for p in dict.keys():
            p_loc = initial_state["packages"][p][0]
            want_man = 0
            for man in initial_state["clients"]:
                if p in initial_state["clients"][man]["packages"]:
                    want_man = man
                    break
            if want_man != 0:
                man_loc = initial_state["clients"][man]["path"]
                dis = math.inf
                for man_place in man_loc:
                    temp_dis = abs(man_place[0]-p_loc[0]) + abs(man_place[1]-p_loc[1])
                    if temp_dis < dis:
                        dis = temp_dis
                dict[p] += dis #distance from man
        return dict

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = self.string_to_dic(state)
        movements = self.move_check(state)
        pick_ups = self.pickup_check(state)
        delivering = self.delivery_check(state)
        waiting = self.wait_check(state)
        temp = movements, pick_ups, delivering, waiting
        temp = self.make_tuple(temp)
        temp = self.is_vaild_action(temp)
        return temp

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state = self.string_to_dic(state)
        for act in action:
            ty = act[0]
            drone = act[1]

            if ty == "move":
                state["drones"][drone][0] = act[2]
            if ty == "pick up":
                if state["drones"][drone][1] == "empty":
                    state["drones"][drone][1] = act[2]
                    state["packages"][act[2]][1] = drone
                    self.package_rank[act[2]] -= 1
                else:
                    state["drones"][drone][2] = act[2]
                    state["packages"][act[2]][1] = drone
            if ty == "deliver":
                state["drones"][drone] = ["empty" if x == act[3] else x for x in state["drones"][drone]]
                state["recieved"].append(act[3])
                del state["packages"][act[3]]
                self.package_rank[act[3]] = 0
            self.all_client_plus_one(state)
        self.t += 1
        new_state = self.dic_to_string(state)
        self.turn += 1
        return new_state

    def all_client_plus_one(self, state):
        for man in state["clients"]:
            state["clients"][man]["position_index"] = (state["clients"][man]["position_index"]+1) % len(state["clients"][man]["path"])

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        # after performing the action (e.g deliver) check for finishing.
        state = self.string_to_dic(state)
        #for v in state["clients"].values():
        #    for p in v["packages"]:
        #        if p not in v["recieved"]:
        #            return False  # someone didn't get yet his package
        if len(state["recieved"]) == self.total_wanted_packages:
            return True
        return False

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        # h = 0
        # actions = node.action
        # state = self.string_to_dic(node.state)
        # if len(self.pick_flag) > 0:
        #     for i in self.drones_loc(state):
        #         h+= self.move_score[i[0]][i[1]]
        # return h
        # if len(self.pick_flag) > 0:
        #     if actions is None:
        #         return h
        #     for i in actions:
        #         if i[0] == 'deliver':
        #             return 0
        #         if i[0] == 'pick up':
        #             if i[2] in self.pick_flag:
        #                 self.pick_flag.remove(i[2])
        #                 return 0
        #             else:
        #                 return 100
        #         if i[0] == "wait":
        #             h += self.M
        #         if i[0] == "move":
        #             h += (self.move_score[i[2][0]][i[2][1]]) *2
        #     return h
        # else:
        #     if actions is None:
        #         return h
        #     for i in actions:
        #         if i[0] == 'deliver':
        #             return 0
        #         if i[0] == 'pick up':
        #             return 100
        #         if i[0] == "wait":
        #             h += self.M
        #         if i[0] == "move":
        #             h += self.l1(i[2], )
        #     return h







        h = 0
        state = self.string_to_dic(node.state)
        for i in self.drones_loc(state):
            h+= self.move_score[i[0]][i[1]]
        for p in self.relevant_pakages:
            if p in state["packages"].keys():
                if state["packages"][p][1] == 'floor':
                    h += 2 * (self.M + self.N)
                else:
                    drone_name = state["packages"][p][1]
                    p_loc = state["drones"][drone_name][0]
                    if p_loc in state["clients"][self.package_match[p]]["path"]:
                        h+=2
                    else:
                        h += (self.M + self.N)
        actions = node.action
        if actions is None:
            return h
        for i in actions:
            if i[0] == 'deliver':
                return 0
            if i[0] == "wait":
                h+= 6
            if i[0] == "move":
                h+= (self.move_score[i[2][0]][i[2][1]])*0.19
        return h

    def make_move_grid(self, state):
        N = len(state["map"])
        M = len(state["map"][0])
        c = [[1 for col in range(M)] for row in range(N)]
        def l1(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def relevant_pak(state):
            tmp = []
            for i in state["clients"].keys():
                for j in state["clients"][i]["packages"]:
                    tmp.append(j)
            return tmp

        def pac_q(state):
            d = []
            relevant = self.relevant_pakages
            for i in relevant:
                d.append(state["packages"][i])
            return d



        def score(q, pac_q):
            a = []
            for i in pac_q:
                a.append(l1(i, q))
            return a

        packages_q = pac_q(state)
        for i in range(N):
            for j in range(M):
                c[i][j] = min(score((i, j), packages_q))
        return c



    def drones_loc(self, state):
        q = []
        for i in state["drones"].keys():
            q.append(state["drones"][i][0])
        return q

    def drones_loc_empty(self, state_c, state_p):
        h = 0
        for i in state_c["drones"].keys():
            if ("empty" == state_c["drones"][i][1]) and ("empty" == state_c["drones"][i][2]):
                if state_c["drones"][i][0] == state_p["drones"][i][0]:
                    h+=1
        return h

    def l1(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def relevant_pak(self, state):
        tmp = []
        for i in state["clients"].keys():
            for j in state["clients"][i]["packages"]:
                tmp.append(j)
        return tmp

    def wait_check(self, state):
        waiting = ()
        for drone in state["drones"].keys():
            waiting += (("wait", drone),)
        return waiting

    def is_vaild_action(self, actions):
        # check if 2 drones try to pickup the same package
        temp = []
        for row in actions:
            row_flag = True
            to_pick_up = set()
            for act in row:
                if act[0] == "pick up":
                    if act[2] not in to_pick_up:
                        to_pick_up.add(act[2])
                    else:
                        row_flag = False
                        break
            if row_flag:
                temp.append(row)
        return tuple(temp)

    def move_check(self, state):
        actions = ()
        for drone in state["drones"].keys():
            drone_q = state["drones"][drone][0]
            # check what is valid - not Impasable, not out of grid
            if  self.possible_move(state,(drone_q[0] - 1, drone_q[1])) :
                actions += (("move", drone, (drone_q[0] - 1, drone_q[1])),)  # notice the comma!
            if  self.possible_move(state,(drone_q[0] + 1, drone_q[1])):
                actions += (("move", drone, (drone_q[0] + 1, drone_q[1])),)  # notice the comma!
            if self.possible_move(state,(drone_q[0] , drone_q[1] - 1)):
                actions += (("move", drone, (drone_q[0] , drone_q[1] - 1)),)  # notice the comma!
            if self.possible_move(state,(drone_q[0], drone_q[1] + 1)) :
                actions += (("move", drone, (drone_q[0], drone_q[1] + 1)),)  # notice the comma!
        return actions

    def possible_move(self, state, move):
        if move[0] < self.N and move[1] < self.M and move[0] >= 0 and move[1] >= 0:
            if self.map[move[0]][move[1]] == "P":
                return True
        return False

    def pickup_check(self, state):
        # pre conditions: package on floor, room to carry, closenees.
        actions = ()
        for drone in state["drones"].keys():
            drone_q = state["drones"][drone][0]
            if state["drones"][drone][1] == 'empty' or state["drones"][drone][2] == 'empty':
                for package in state["packages"].keys():
                    package_q = state["packages"][package][0]
                    if package_q[0] == drone_q[0] and package_q[1] == drone_q[1] and state["packages"][package][1] == 'floor' and package in self.relevant_pakages:
                        actions += (("pick up", drone, package),)
        return actions

    def delivery_check(self, state):
        # pre conditions:  package is on drone + client in same area + client want this package
        actions = ()
        for drone in state["drones"].keys():
            for man in state["clients"].keys():
                for package in state["clients"][man]["packages"]:
                    if package not in state["recieved"] and (
                            package == state["drones"][drone][1] or package == state["drones"][drone][2]):
                        if self.current_loc(state["clients"][man]) == state["drones"][drone][0]:
                            actions += (("deliver", drone, man, package),)
        return actions

    def current_loc(self, man):
        return man["path"][man["position_index"]]

    def make_tuple(self, test1):
        c = set()
        for i in test1:
            for j in i:
                c.add(j[1])
        b = {a: [] for a in c}
        for i in test1:
            for j in i:
                b[j[1]].append(j)
        d = [i for i in b.values()]
        e = tuple(product(*d))
        return e

    def dic_to_string(self, dictionary):
        return repr(dictionary)

    def string_to_dic(self, str):
        return ast.literal_eval(str)


    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_drone_problem(game):
    return DroneProblem(game)

