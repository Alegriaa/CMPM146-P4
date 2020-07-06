from copy import deepcopy
import logging


def log_execution(fn):
    def logged_fn(self, state):
        logging.debug('Executing:' + str(self))
        result = fn(self, state)
        logging.debug('Result: ' + str(self) + ' -> ' + ('Success' if result else 'Failure'))
        return result
    return logged_fn

# Do not use the Node or Composite classes. These are abstract classes used for the other node types. 
############################### Base Classes ##################################
class Node:
    def __init__(self):
        raise NotImplementedError

    def execute(self, state):
        raise NotImplementedError

    def copy(self):
        return deepcopy(self)


class Composite(Node):
    def __init__(self, child_nodes=[], name=None):
        self.child_nodes = child_nodes
        self.name = name

    def execute(self, state):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.name if self.name else ''

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        for child in self.child_nodes:
            if hasattr(child, 'tree_to_string'):
                string += child.tree_to_string(indent + 1)
            else:
                string += '| ' * (indent + 1) + str(child) + '\n'
        return string


############################### Composite Nodes ##################################
#Selector  -  a  branching  node  containing  an  ordered  list  of  child  nodes. 
#  When  the selector node is executed, it will attempt executing its child nodes in 
# order until one returns a success (True). Once a child returns a success, 
# it skips the execution of the remaining child nodes. 
class Selector(Composite):
    @log_execution
    def execute(self, state):
        for child_node in self.child_nodes:
            success = child_node.execute(state)
            if success:
                return True
        else:  # for loop completed without success; return failure
            return False

# Sequence  -  a  branching  node  containing  an  ordered  list  of  child  nodes.  
# When  the sequence node is executed, it will attempt executing its child nodes 
# in order until one returns a failure (False). Once a child returns a failure, 
# the sequence is aborted. 
class Sequence(Composite):
    @log_execution
    def execute(self, state):
        for child_node in self.child_nodes:
            continue_execution = child_node.execute(state)
            if not continue_execution:
                return False
        else:  # for loop completed without failure; return success
            return True


############################### Leaf Nodes ##################################
# Check - a leaf node which contains a check function, i.e. 
# a function which checks for a condition within the state. 
# These function calls should not issue orders.
class Check(Node):
    def __init__(self, check_function):
        self.check_function = check_function

    @log_execution
    def execute(self, state):
        return self.check_function(state)

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.check_function.__name__

# Action - a leaf node which contains an action function, 
# typically issuing one or more orders.
class Action(Node):
    def __init__(self, action_function):
        self.action_function = action_function

    @log_execution
    def execute(self, state):
        return self.action_function(state)

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.action_function.__name__

# Optional: Using the established classes, 
# implement behavior tree nodes for Decorator types   
# (such   as   Inverter/LoopUntilFailed/AlwaysSucceed/etc)  
#  and/or   Random Selector. 
