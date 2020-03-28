import math
import logging

logging.basicConfig(filename='logger.log', level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

class Activity:
    def __init__(self, name, duration):
        logging.info("new activity has been created, name: " + name + ", duration: " + str(duration))
        self.name = str(name).lower()
        self.duration = duration
    
    # question 6:
    # str method for activity
    def __str__(self):
        logging.info("str method called for '" + self.name + "' activity")
        return "Activity Name: " + self.name + ", Duration: " + str(self.duration)


    def __repr__(self):
        logging.info("repr method called for '" + self.name + "' activity")
        return self.name

class Pert:
    # question 1:
    # a graph is a map with activities as keys and list of outgoing activities as value for every key
    # the graph starts with a 'start' node and ends with a 'end' node
    # see example below
    def __init__(self, graph={}):
        logging.info("new pert: '" + repr(self) + "' has been created, graph: " + str(graph))
        self.forward_dict = graph   # list of out going nodes for every activity
        self.backward_dict = {}     # list of in going nodes for every activity
        self.info_dict = {}         # map of details for every activity
        self.start_activity = Activity
        self.end_activity = Activity
        self.reset_initial_graph()  # first reset of the graph
        self.generate_info()        # enetering values into 'info_dict'

    # question 6:
    # str method for pert
    def __str__(self):
        logging.info("str method called for '" + repr(self) + "' pert")
        iterator = iter(self)
        graph_str = 'Activities:\n'
        for activity in iterator:
            graph_str += str(activity) + '\n'
        return (graph_str + 'Connections:\n' 
            + str(self.forward_dict)
            + '\nProject Duration:\n' 
            + str(self.info_dict[self.end_activity]['ef']))

    # question 7:
    # iterator for the pert class
    def __iter__(self):
        logging.info("new iterator for '" + repr(self) + "' pert")
        return iter(self.forward_dict)

#################################################################################################################################
#################################################################################################################################
#################################################################################################################################

    # reseting 'backward_dict' for every activity
    # setting 'start_activity' and 'end_activity'
    def reset_initial_graph(self):
        logging.info("'reset_initial_graph' method has been called for '" + repr(self) + "' pert")
        for activity in self.forward_dict:
            self.backward_dict[activity] = []
        for activity in self.forward_dict:
            if activity.name == "start":
                self.start_activity = activity
            if activity.name == "end":
                self.end_activity = activity
            for node in self.forward_dict[activity]:
                self.backward_dict[node].append(activity)
        self.reset_info()

    # duration: the duration of the activity
    # es: early start
    # ef: early finish
    # ls: late start
    # lf: late finish
    # slack: lf - ef or ls - es
    def reset_info(self):
        logging.info("'reset_info' method has been called for '" + repr(self) + "' pert")
        for activity in self.forward_dict:
            self.info_dict[activity] = {
                "duration": activity.duration, 
                "es": 0, "ef": 0, "ls": 0, "lf": math.inf, 
                "slack": 0}

    # run from start to end and put all 'es' 'ef' details in place
    # run from end to start and put all 'ls' 'lf' details in place
    # calculate slack for all activities (except isolated)
    # caclculate details for isolated activities
    def generate_info(self):
        logging.info("'generate_info' method has been called for '" + repr(self) + "' pert")
        if self.forward_dict == {}:
            return
        self.info_dict[self.start_activity]["ef"] = self.info_dict[self.start_activity]["duration"]
        self.start_to_end_scan(self.start_activity)
        self.info_dict[self.end_activity]["lf"] = self.info_dict[self.end_activity]["ef"]
        self.info_dict[self.end_activity]["ls"] = self.info_dict[self.end_activity]["lf"] - self.info_dict[self.end_activity]["duration"]
        self.end_to_start_scan(self.end_activity)
        self.clatulate_slack()
        self.generate_info_for_isolated()

    # run from start to end and put all 'es' 'ef' details in place
    def start_to_end_scan(self, activity):
        logging.info("'start_to_end_scan' method has been called for '" + repr(self) + "' pert")
        for node in self.forward_dict[activity]:
            if self.info_dict[activity]["ef"] > self.info_dict[node]["es"]:
                self.info_dict[node]["es"] = self.info_dict[activity]["ef"]
                self.info_dict[node]["ef"] = self.info_dict[node]["es"] + self.info_dict[node]["duration"]
            self.start_to_end_scan(node)

    # run from end to start and put all 'ls' 'lf' details in place
    def end_to_start_scan(self, activity):
        logging.info("'end_to_start_scan' method has been called for '" + repr(self) + "' pert")
        for node in self.backward_dict[activity]:
            if (self.info_dict[node]["lf"] > self.info_dict[activity]["ls"]):
                self.info_dict[node]["lf"] = self.info_dict[activity]["ls"]
                self.info_dict[node]["ls"] = (self.info_dict[node]["lf"] - self.info_dict[node]["duration"])
            self.end_to_start_scan(node)

    # calculate slack for all activities (except isolated)
    def clatulate_slack(self):
        logging.info("'clatulate_slack' method has been called for '" + repr(self) + "' pert")
        for activity in self.forward_dict:
            self.info_dict[activity]["slack"] = self.info_dict[activity]["lf"] - self.info_dict[activity]["ef"]

    # caclculate details for isolated activities
    # assumption: activity duration shorter than project duration
    def generate_info_for_isolated(self):
        logging.info("'generate_info_for_isolated' method has been called for '" + repr(self) + "' pert")
        isolated = self.find_isolated()
        for activity in isolated:
            self.info_dict[activity]["ef"] = self.info_dict[activity]["es"] + self.info_dict[activity]["duration"]
            self.info_dict[activity]["lf"] = self.info_dict[self.end_activity]["lf"]
            self.info_dict[activity]["ls"] = self.info_dict[activity]["lf"] - self.info_dict[activity]["duration"]
            self.info_dict[activity]["slack"] = self.info_dict[activity]["lf"] - self.info_dict[activity]["ef"]

#################################################################################################################################
#################################################################################################################################
#################################################################################################################################

    # question 2:
    # add activity to the pert
    def add_activity(self, activity, in_connections=[], out_connections=[]):
        logging.info("'add_activity' method has been called for '" + repr(self) + "' pert")
        if activity in self.forward_dict:
            return
        self.forward_dict[activity] = out_connections
        self.backward_dict[activity] = in_connections
        if in_connections != []:
            for node in in_connections:
                if self.forward_dict[node] is None:
                    self.forward_dict[node] = []
                self.forward_dict[node] += [activity]
        if out_connections != []:
            for node in out_connections:
                if self.backward_dict[node] is None:
                    self.backward_dict[node] = []
                self.backward_dict[node] += [activity]
        self.info_dict[activity] = {
            "duration": activity.duration, 
            "es": 0, "ef": 0, "ls": 0, "lf": math.inf, 
            "slack": 0}
        self.reset_info()
        self.generate_info()

    # question 3:
    # find isolated activities
    def find_isolated(self):
        logging.info("'find_isolated' method has been called for '" + repr(self) + "' pert")
        isolated = list(self.info_dict)
        for activity in self.forward_dict:
            if self.forward_dict[activity] != [] and activity in isolated:
                isolated.remove(activity)
        for activity in self.backward_dict:
            if self.backward_dict[activity] != [] and activity in isolated:
                isolated.remove(activity)
        return isolated
    
    # question 4:
    # get slack time for each activity in descending order without critical activities
    def get_slack_for_each_activity(self):
        logging.info("'get_slack_for_each_activity' method has been called for '" + repr(self) + "' pert")
        slacks = {activity: self.info_dict[activity]["slack"] for activity in self.info_dict if self.info_dict[activity]["slack"] != 0}
        return sorted(slacks.items(), key=lambda kv: kv[1], reverse=True)
    
    # question 5:
    # get the sum of all the slacks in the project
    def get_sum_of_slacks(self):
        logging.info("'get_sum_of_slacks' method has been called for '" + repr(self) + "' pert")
        slacks = [kv[1] for kv in self.get_slack_for_each_activity()]
        return sum(slacks)

    # get the critical path as list
    def get_critical_path(self):
        logging.info("'get_critical_path' method has been called for '" + repr(self) + "' pert")
        activity = self.start_activity
        path = [activity]
        while activity != self.end_activity :
            for node in self.forward_dict[activity]:
                if self.info_dict[node]["slack"] == 0:
                    activity = node
            path += [activity]
        return path

    # question 8:
    # get the critical path with length as map
    def get_critical_path_with_length(self):
        logging.info("'get_critical_path_with_length' method has been called for '" + repr(self) + "' pert")
        return {activity: activity.duration for activity in self.get_critical_path()}
    
    # question 9:
    # get a map of the activities with the maximum amount of time to reduce from it's duration without taking it our of the critical path
    # we are getting all alternative paths between 2 nodes (activities) in the critical path (only nodes that have at least one node between them)
    # we are taking the minimum slack and putting it as the value for maximum reduction
    # the minimum duration for every task is 1
    def shorten_critical_path(self):
        logging.info("'shorten_critical_path' method has been called for '" + repr(self) + "' pert")
        critical_path = self.get_critical_path()
        max_decrease_to_activities = {activity: activity.duration - 1 for activity in critical_path}
        for i in range(0,  len(critical_path), 1):
            for j in range(2, len(critical_path) - i, 1):
                for path in self.get_all_alternative_paths(critical_path[i], critical_path[i + j]):
                    for activity in critical_path[i + 1 : i + j : 1]:
                        if path[1] not in critical_path and max_decrease_to_activities[activity] >= self.info_dict[path[1]]["slack"]:
                            max_decrease_to_activities[activity] = self.info_dict[path[1]]["slack"] - 1
        return max_decrease_to_activities

    # get all the paths between 2 nodes (activities) in the graph (pert)
    def get_all_alternative_paths(self, start_activity, end_activity, path=[]):
        logging.info("'get_all_alternative_paths' method has been called for '" + repr(self) + "' pert")
        one_path = path + [start_activity]
        if start_activity == end_activity:
            return [one_path]
        if start_activity not in self.info_dict:
            return []
        paths = []
        for activity in self.forward_dict[start_activity]:
            paths += self.get_all_alternative_paths(activity, end_activity, one_path)
        return paths

if __name__ == "__main__":
    start = Activity("start", 5)
    a = Activity("a", 2)
    b = Activity("b", 3)
    c = Activity("c", 3)
    d = Activity("d", 4)
    e = Activity("e", 3)
    f = Activity("f", 6)
    end = Activity("end", 2)
    graph = {start: [a, d, f], a: [b], b: [c], c: [end], d: [e], e: [end], f:[end], end:[]}
    # question 1: initializin a graph
    print("initialize a graph:")
    pert = Pert(graph)
    # question 2: add activity
    j = Activity("j", 16)
    print("add activity to project:")
    pert.add_activity(j, [start], [end])
    # question 6: print activity with str
    print("print activity:")
    print(j)
    # question 8: critical path
    print("critical path:")
    print(pert.get_critical_path())
    # question 9: maximum shorting times
    print("maximum shorting times:")
    print(pert.shorten_critical_path())
    # question 4: slack time for each activity
    print("slack time in descending order:")
    print(pert.get_slack_for_each_activity())
    # question 5: sum of slack times
    print("sum of slack times:")
    print(pert.get_sum_of_slacks())
    # question 7: iterate on the nodes with iterator
    print("iterate over all the activities with iterator:")
    for activity in iter(pert):
        print(activity)
    # question 3: isolated activities
    print("isolated activities:")
    print(pert.find_isolated())
    # print pert
    print("print pert:")
    print(pert)
