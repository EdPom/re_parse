# File Name : FA.py
# Description : THis file specifies the data structure of
#     class FInite Automata.

def CheckID(ID):
    # States are named with their ID (an integer)
    # Check the given ID is valid
    if type(ID) is not int:
        raise TypeError('ID should be an integer.')
    if ID < 0:
        raise ValueError('ID should be non-negative.')

class State:
    """Representation of states in a finite automata."""

    def __init__(self, ID):
        # Transitions of a state is recorded as a 
        # dictionary. The key being the condiion (a
        # character) and the value being the ID of 
        # destination state.
        CheckID(ID)
        
        self.TransitionMap = dict()
        self.ID = ID
    
    def SetTransition(self, key, DestID):
        """Use this function to specify each transition,
        which includes the condition of transition (a
        character) and the destination of the transition
        (the ID of the destination state)."""
        # Question: how do I check if DestID is valid?
        CheckID(DestID)
        
        try:
            self.TransitionMap[key]
        except KeyError:
            self.TransitionMap[key] = list()
        
        if DestID not in self.TransitionMap[key]:
            self.TransitionMap[key].append(DestID)
        
        # Sucess
        return True
    
    def Print(self):
        """Used as a debugging tool. This function
        prints out all information of this state"""
        print "State ID:", self.ID

        for key in self.TransitionMap.keys():
            print '\t',key,'=>',self.TransitionMap[key]

class FiniteAutomata:
    """Representation of the Finite Automata."""
    
    def __init__(self):
        self.States = list()
        self.StartState = list()
        self.AcceptState = list()

    def FindStateByID(self, ID):
        # print "ID =", ID
        # val = list()
        # for state in self.States:
        #     if state.ID == ID:
        #         val.append(state)
        # return val
        return [state for state in self.States if state.ID == ID]
    
    def AddState(self, state):
        # There shouldn't be a state with the same ID
        if len(self.FindStateByID(state.ID)) is not 0:
            print "State with the same ID already exist."
        self.States.append(state)
        # Place states in the order of their ID
        sorted(self.States, key=lambda state: state.ID)
    
    def SetAcceptState(self, ID):
        """Add the state with its id being ID to
        accepting states"""
        CheckID(ID)
        self.AcceptState.append(ID)
    
    def SetStartState(self, ID):
        """Set the state with id being ID to be the start
        state"""
        CheckID(ID)
        self.StartState.append(ID)

    def GetStates(self):
        # return [state for state in self.States]
        return self.States[:]
    
if __name__ == '__main__':
    # State 1 should have two conditions: on encountering
    # character 'a', there should be transition to state
    # 2 and 3, on encountering 'b', there should be a
    # transition to state 3.
    state = State(1)
    state.SetTransition('a', 2)
    # a redundent operation
    state.SetTransition('a', 2)
    state.SetTransition('a', 3)
    state.SetTransition('b', 3)
    # state.Print()

    fa = FiniteAutomata()
    fa.AddState(state)
    fa.AddState(State(2))
    fa.SetAcceptState(2)
    fa.SetStartState(1)
    # for state in fa.FindStateByID(3):
    #     state.Print()
    # print fa.GetStates()

    # This should raise an exception of type error
    # State('a')

    # This should raise an exception of value error
    # State(-1)