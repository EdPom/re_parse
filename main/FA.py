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
        # CheckID(ID)
        
        self.TransitionMap = dict()
        self.ID = ID
    
    def SetTransition(self, key, DestID):
        """Use this function to specify each transition,
        which includes the condition of transition (a
        character) and the destination of the transition
        (the ID of the destination state)."""
        # Question: how do I check if DestID is valid?
        # CheckID(DestID)
        
        # try:
        #     self.TransitionMap[key]
        # except KeyError:
        if key not in self.TransitionMap:
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
    
    def __init__(self, ID):
        self.States = list()
        self.StateCounter = 0
        self.TransitionMap = dict()
        self.StartState = list()
        self.AcceptState = list()
        self.ID = ID

    # def FindStateByID(self, ID):
    #     # print "ID =", ID
    #     # val = list()
    #     # for state in self.States:
    #     #     if state.ID == ID:
    #     #         val.append(state)
    #     # return val
    #     return [state for state in self.States if state.ID == ID]
    
    def AddState(self):
        # There shouldn't be a state with the same ID
        # if len(self.FindStateByID(state.ID)) is not 0:
        #     print "State with the same ID already exist."
        StateID = str(self.ID) + '_' + str(self.StateCounter)
        state = State(StateID)
        self.States.append(state)
        # # Place states in the order of their ID
        sorted(self.States, key=lambda stateID: stateID)

        self.StateCounter += 1
        return StateID

    def FindStatePosByID(self, ID):
        for idx, state in enumerate(self.States):
            if state.ID == ID:
                return idx
        return -1
    
    def AddTransition(self, src, dest, char):
        """set transition on given character for a state."""
        srcpos = self.FindStatePosByID(src)
        destpos = self.FindStatePosByID(dest)

        if srcpos < 0 or destpos < 0:
            # print "ERROR: State ID out of bound."
            return False

        # key = str(self.ID) + '_' + str(src)
        # self.TransitionMap[key] = str(self.ID) + '_' + str(dest)

        self.States[srcpos].SetTransition(char, dest)
        return True
    
    def SetAcceptState(self, ID):
        self.AcceptState.append(ID)
    
    def GetAcceptState(self):
        return self.AcceptState[:]
    
    def SetStartState(self, ID):
        self.StartState.append(ID)

    def GetStartState(self):
        return self.StartState[:]

    # def GetStates(self):
    #     return self.States[:]

class FiniteAutomataManager:

    def __init__(self):
        self.FACounter = 0
        self.FAs = list()
    
    def CreateFA(char):
        fa = FiniteAutomata(self.FACounter)
        s1 = fa.AddState()
        s2 = fa.AddState()
        fa.AddTransition(s1, s2, char)
        fa.SetAcceptState(s2)
        fa.SetStartState(s1)
        self.FACounter += 1

        return fa
    
if __name__ == '__main__':

    fa = FiniteAutomata(0)
    s1 = fa.AddState()
    s2 = fa.AddState()
    fa.AddTransition(s1, s2, 'a')
    fa.SetAcceptState(s2)
    fa.SetStartState(s1)