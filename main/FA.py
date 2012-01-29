# File Name : FA.py
# Description : THis file specifies the data structure of
#     class FInite Automata.

# acquired from stackoverflow: "How do you remove duplicates from
# a list in Python whilst preserving order?""
# I made a mistake here: this funtion is used to remove lists with
# the first item being the same, so it's not suitable for my use here
# 
# def UniqueElem(seq):
#     seen = set()
#     seen_add = seen.add
#     return [ x for x in seq if x not in seen and not seen_add(x)]

# Get this from 'Yet Another Unique() Function' at ActiveState Code
# http://code.activestate.com/recipes/502263/#c2
# This works for list of lists
def UniqueElem(inlist, keepstr=True):
    typ = type(inlist)
    if not typ == list:
        inlist = list(inlist)
    i = 0
    while i < len(inlist):
        try:
          del inlist[inlist.index(inlist[i], i + 1)]
        except:
          i += 1
    if not typ in (str, unicode):
        inlist = typ(inlist)
    else:
        if keepstr:
          inlist = ''.join(inlist)
    return inlist



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
    
    def GetTransition(self, key):
        if key in self.TransitionMap:
            return self.TransitionMap[key]
        else:
            return list()
    
    def Print(self):
        """Used as a debugging tool. This function
        prints out all information of this state"""
        print "State ID:", self.ID

        for key in self.TransitionMap.keys():
            print '\t',key,'=>',self.TransitionMap[key]

class FiniteAutomata:
    """Representation of the Finite Automata."""
    
    def __init__(self, ID, char):
        """create a NFA for single character transition."""
        self.States = list()
        self.StateCounter = 0
        self.TransitionMap = dict()
        self.StartState = list()
        self.AcceptState = list()
        self.ID = ID

        # Create an FA for this character
        s1 = self.AddState()
        s2 = self.AddState()
        self.AddTransition(s1, s2, char)
        self.SetAcceptState(s2)
        self.SetStartState(s1)
    
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
        """This function return the position of the index in
        the list 'States' when its ID is matched."""
        for idx, state in enumerate(self.States):
            # state ID is assumed to be unique in the list
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
    
    def CreateClosure(self):
        """create the NFA of closure of the current FA"""

        if len(self.StartState) != 1:
            print "ERROR: More than one start state."
            exit()
        if len(self.AcceptState) != 1:
            print "WARNING: More than one accepting state."
            exit()

        NewStart = self.AddState()
        NewEnd = self.AddState()
        OldStart = self.StartState.pop()
        OldEnd = self.AcceptState.pop()

        # 4 new transitions:
        # 
        #           (new)
        #         +------+
        #         |      |
        #   (new) |      v (new)
        # (1) -> (2) -> (3) -> (4)
        #  |                    ^
        #  |                    |
        #  +--------------------+
        #           (new)
        
        self.AddTransition(NewStart, OldStart, 'EPSILON')
        self.AddTransition(OldEnd, NewEnd, 'EPSILON')
        self.AddTransition(OldEnd, OldStart, 'EPSILON')
        self.AddTransition(NewStart, NewEnd, 'EPSILON')

        self.StartState.append(NewStart)
        self.AcceptState.append(NewEnd)
    
    def CreateConcatenation(self, fa2):
        if len(self.StartState) != 1 or len(fa2.StartState) != 1:
            print "ERROR: More than one start state."
            exit()
        if len(self.AcceptState) != 1 or len(fa2.AcceptState) != 1:
            print "WARNING: More than one accepting state."
            exit()
        
        # transfer all states of fa2 into fa1
        self.States.extend(fa2.States)

        # NewStart = self.AddState()
        # NewEnd = self.AddState()
        OldStart = self.StartState.pop()
        OldEnd = self.AcceptState.pop()
        OldStart2 = fa2.StartState.pop()
        OldEnd2 = fa2.AcceptState.pop()

        # 1 new transition:
        # end of fa1 -> start of fa2
        self.AddTransition(OldEnd2, OldStart, 'EPSILON')

        self.StartState.append(OldStart2)
        self.AcceptState.append(OldEnd)
    
    def CreateAlternation(self, fa2):
        if len(self.StartState) != 1 or len(fa2.StartState) != 1:
            print "ERROR: More than one start state."
            exit()
        if len(self.AcceptState) != 1 or len(fa2.AcceptState) != 1:
            print "WARNING: More than one accepting state."
            exit()
        
        # transfer all states of fa2 into fa1
        self.States.extend(fa2.States)

        NewStart = self.AddState()
        NewEnd = self.AddState()
        OldStart = self.StartState.pop()
        OldEnd = self.AcceptState.pop()
        OldStart2 = fa2.StartState.pop()
        OldEnd2 = fa2.AcceptState.pop()

        # 4 new transition:
        # new start -> 2 old starts
        # 2 old ends -> new end
        self.AddTransition(NewStart, OldStart, 'EPSILON')
        self.AddTransition(NewStart, OldStart2, 'EPSILON')
        self.AddTransition(OldEnd, NewEnd, 'EPSILON')
        self.AddTransition(OldEnd2, NewEnd, 'EPSILON')

        self.StartState.append(NewStart)
        self.AcceptState.append(NewEnd)

    def FindEpsilonClosure(self, StateID):
        
        EpsilonSet = [StateID,]

        idx = 0
        while idx < len(EpsilonSet):
            StatePos = self.FindStatePosByID(EpsilonSet[idx])
            EpsilonSet.extend(self.States[StatePos].GetTransition('EPSILON'))

            idx += 1
        
        return sorted(EpsilonSet[:])

    def FindEpsilonClosureList(self, StateIDs):
        
        EpsilonSet = StateIDs

        idx = 0
        while idx < len(EpsilonSet):
            StatePos = self.FindStatePosByID(EpsilonSet[idx])
            EpsilonSet.extend(self.States[StatePos].GetTransition('EPSILON'))

            idx += 1
        
        return sorted(EpsilonSet[:])
    
    def FindTransitionList(self, StateIDs, char):
        Dest = list()
        for state in StateIDs:
            StatePos = self.FindStatePosByID(state)
            Dest.extend(self.States[StatePos].GetTransition(char))
        
        # get this from stackoverflow : "Removing duplicates from list of
        # lists in Python"
        return UniqueElem(Dest)

    def SetAcceptState(self, ID):
        self.AcceptState.append(ID)
    
    def GetAcceptState(self):
        return self.AcceptState[:]
    
    def SetStartState(self, ID):
        self.StartState.append(ID)

    def GetStartState(self):
        return self.StartState[:]

    def Print(self):
        for state in self.States:
            state.Print()

    
if __name__ == '__main__':

    fa = FiniteAutomata(0, 'a')
    fa2 = FiniteAutomata(1, 'b')
    fa3 = FiniteAutomata(2, 'c')
    fa.CreateAlternation(fa2)
    fa.CreateAlternation(fa3)
    print fa.FindEpsilonClosure(fa.GetStartState().pop())
    # fa.Print()

