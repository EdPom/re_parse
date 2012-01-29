# File Name : parser.py
# Description : This file implements the main parser
#     functionality.
import FA
import rule


class Parser:
    """This is the parser class. It implements the main
    functionality"""

    def __init__(self, exp=None):
        """This function implements the initialization
        process of the parser class."""

        # invalid input is now handled in ScanRE
        self.DefineRE(exp)

        # These functions are moved to DefineRE(), so they can be triggered
        # after defining new regular expressions
        # self.REtoNFA()
        # self.NFAtoDFA()
        # self.MinimizeDFA()

        
    def ScanRE(self, exp):
        """Used to parse the regular expression into an
        intermediate representation."""
        # Make sure the expression is not empty
        assert type(exp) is str 
        assert exp
        
        self.NotedRE = list()

        i = 0
        while i < len(exp):
            if exp[i] == ' ':
                i += 1
            elif exp[i] == '\\':
                ch = exp[i:i + 2]
                i += 2
            else:
                ch = exp[i]
                i += 1
            
            self.NotedRE.append(rule.CheckCharType(ch))


    def DefineRE(self, exp):
        """This function take the regular expression as input,
        and transforms it internally."""

        # Clean old RE and its DFA (if it exist)
        # try:
        #     del self.FA
        # except AttributeError:
        #     pass

        # process the new RE
        self.Stack = list()
        # should tell the user if there's error
        self.ScanRE(exp)

        self.REtoNFA()
        self.NFAtoDFA()
        self.MinimizeDFA()
    
    def REtoNFA(self):
        """This function transforms a regular expression to
        a non-deterministic finite automata (NFA) using the
        method "Thompson's Construction"."""

        def AddConcatToNotedRE(NotedRE):
            """concatenations are not denoted explicitly
            in the original regular expression, so we
            add them to the RE in here."""

            assert NotedRE
            
            ModifiedRE = list()
            LastType = None
            for idx, (Type, Value) in enumerate(NotedRE):
                if LastType == 'LEFT_SQUARE_BRACKET':
                    InBracket = True
                elif LastType == 'RIGHT_SQUARE_BRACKET':
                    InBracket = False
                elif LastType is None:
                    InBracket = False
                if idx > 0 and rule.CheckConcatenation(Type,
                                                  LastType,
                                                  InBracket):
                    ModifiedRE.append(('CONCATENATION', None))
                ModifiedRE.append((Type, Value))
                
                LastType = Type
            return ModifiedRE[:]
        
        def ConvertREToAlter(NotedRE):
            ModifiedRE = list()
            FlagDash = False
            for idx, (Type, Value) in enumerate(NotedRE):
                if not FlagDash:
                    if Type == 'DASH':
                        if idx > 0 and idx != len(NotedRE) - 1:
                            FlagDash = True
                            CharFrom = NotedRE[idx - 1][1]
                            PosFrom = idx - 1
                        else:
                            ModifiedRE.append(('ALTERNATION', '|'))
                            ModifiedRE.append(('CHARACTER', Value))
                    else:
                        Test2 = rule.IsValidDashOperand(Value)
                        Test3 = idx == len(NotedRE) - 1
                        if Test3 and Test2:
                            ModifiedRE.append(('ALTERNATION', '|'))
                            ModifiedRE.append((Type, Value))
                        elif NotedRE[idx + 1][0] != 'DASH' and Test2:
                            if idx > 0:
                                ModifiedRE.append(('ALTERNATION', '|'))
                            ModifiedRE.append((Type, Value))
                elif FlagDash and rule.IsValidDashOperand(Value):
                    CharTo = Value
                    # if PosFrom > 0:
                    #     print '1'
                    #     ModifiedRE.append(('ALTERNATION', '|'))
                    for idx, (Type, Value) in enumerate(rule.ConvertDashExpression(CharFrom,
                                                             CharTo)):
                        if idx > 0 or PosFrom > 0:
                            ModifiedRE.append(('ALTERNATION', '|'))
                        ModifiedRE.append((Type, Value))
                    FlagDash = False
            
            return ModifiedRE[:]

        def AddAlterToNotedRE(NotedRE):
            """Since alternations are already specified
            explicitly in the regular expression, all
            this function does is to change things inside
            brackets to a string of alternations."""

            assert NotedRE
            
            ModifiedRE = list()
            REToTransform = list()
            LastType = None
            InBracket = False
            for idx, (Type, Value) in enumerate(NotedRE):
                if Type == 'LEFT_SQUARE_BRACKET':
                    InBracket = True
                elif Type == 'RIGHT_SQUARE_BRACKET':
                    InBracket = False
                    ModifiedRE.append(('LEFT_PARENTHESES',
                                       '('))
                    ModifiedRE.extend(ConvertREToAlter(REToTransform))
                    ModifiedRE.append(('RIGHT_PARENTHESES',
                                       ')'))
                    REToTransform = list()

                if Type is not 'RIGHT_SQUARE_BRACKET':
                    if not InBracket:
                        ModifiedRE.append((Type, Value))
                    else:
                        if rule.IsValidDashOperand(Value) or Type == 'DASH':
                            REToTransform.append((Type, Value))
                
                LastType = Type
            return ModifiedRE[:]
        
        def FindLastOpBeforePos(NotedRE, Pos):
            """This function find the position of the
            last operand before the given position"""

            assert NotedRE
            
            Count = 0
            for i in range(Pos - 1, -1, -1):
                if NotedRE[i][0] is 'RIGHT_PARENTHESES':
                    Count += 1
                elif NotedRE[i][0] is 'LEFT_PARENTHESES':
                    Count -= 1
                
                if Count == 0:
                    return i
            
            assert Count == 0


        def ConvertToSimpleRE(NotedRE):
            """This function transforms special
            operators to a combination of simple
            operators ('|', '*', concatenation)"""
            
            assert NotedRE
            
            # At this point, there shouldn't be any
            # square bracket in the RE, so operands
            # are all either in direct form or in
            # parentheses.

            # For now, only the '+' operator is
            # transformed. (It is transformed into
            # one operand in concatenatio with its
            # closure, like a+ = aa*)

            LastRE = NotedRE
            ModifiedRE = list()
            Operand = list()
            idx = 0
            # __counter = 0
            while idx < len(LastRE):
                # if __counter > 100:
                #     print 'ERROR!'
                #     exit()
                # __counter += 1
                if LastRE[idx][0] == 'AT_LEAST_ONE':
                    # find its operand
                    assert idx

                    Pos = FindLastOpBeforePos(LastRE[:idx], idx)
                    # The operand is LastRE[Pos:idx]
                    Operand = LastRE[Pos:idx]
                    # Push things before the operand in the q
                    for Type, Value in LastRE[:Pos]:
                        ModifiedRE.append((Type, Value))
                    # Deal with the operand
                    # op+ = op.op* (. is concat)
                    # push in op
                    for Type, Value in Operand:
                        ModifiedRE.append((Type, Value))
                    # push in concatenation
                    ModifiedRE.append(('CONCATENATION', None))
                    # push in op
                    for Type, Value in Operand:
                        ModifiedRE.append((Type, Value))
                    # push in closure
                    ModifiedRE.append(('CLOSURE', '*'))
                    # Deal with the rest
                    for Type, Value in LastRE[idx+1:]:
                        ModifiedRE.append((Type, Value))
                    LastRE = ModifiedRE[:]
                    ModifiedRE = list()
                    idx = 0

                else:
                    idx += 1

            return LastRE[:]
        
        def CheckPrec(Type, Level, TempStack):

            try:
                PrecHigherThan = rule.CheckPrecedenceHigherThan(Type,
                                                            TempStack[-1][0])
                PrecLessThan = rule.CheckPrecedenceLessThan(Type,
                                                            TempStack[-1][0])
                SameLevel = Level == TempStack[-1][2]
            except IndexError:
                PrecHigherThan = rule.CheckPrecedenceHigherThan(Type, None)
                PrecLessThan = rule.CheckPrecedenceLessThan(Type, None)
                SameLevel = False
            
            return PrecHigherThan, PrecLessThan, SameLevel
        
        # REtoNFA finally starts here...

        # should check if NotedRE exist
        assert self.NotedRE
        
        self.NotedRE = AddConcatToNotedRE(self.NotedRE)
        self.NotedRE = AddAlterToNotedRE(self.NotedRE)
        self.NotedRE = ConvertToSimpleRE(self.NotedRE)
        Stack = list()
        TempStack = list()
        Level = 0
        for Type, Value in self.NotedRE:
            if rule.CheckIsChar(Type):
                # Chars are put into the stack directly
                Stack.append((Type, Value, Level))
            elif Type == 'LEFT_PARENTHESES':
                # Enter the next level
                Level += 1
            elif Type == 'RIGHT_PARENTHESES':
                # all operator has to be put into the stack before we leave
                # this level
                if TempStack:
                    if TempStack[-1][2] == Level:
                        while True:
                            Stack.append(TempStack.pop())
                            if not TempStack or TempStack[-1][2] != Level:
                                break

                Level -= 1
            elif rule.CheckIsOp(Type):
                
                while True:
                    PrecHigherThan, PrecLessThan, SameLevel = CheckPrec(Type,
                                                            Level, TempStack)
                    
                    # operators like closure should be put into stack directly
                    # since they are associated with one operand only, so we don't
                    # have to consider their precedence
                    if rule.CheckIsOneOprandOp(Type):
                        Stack.append((Type, Value, Level))
                        break

                    # otherwise, we can push the previous operator in the stack, but
                    # still can't push the current operator into the stack
                    elif PrecHigherThan and SameLevel:
                        # push into wait stack
                        TempStack.append((Type, Value, Level))
                        break
                    
                    elif PrecLessThan and SameLevel:
                        # pop the first item from wait stack, and compare again
                        Stack.append(TempStack.pop())
                    
                    elif not PrecLessThan and not PrecHigherThan and SameLevel:
                        # pop the first item from wait stack, then push the current
                        # item into wait stack
                        Stack.append(TempStack.pop())
                        TempStack.append((Type, Value, Level))
                        break
                    
                    # if the current operator has higher precedence than the one in
                    # the previous one, than we can't put the operator in the stack
                    # yet since the other operator has not shown up
                    else:
                        TempStack.append((Type, Value, Level))
                        break

            else:
                # Error!
                print 'ERROR: unknown char type.'
                assert False
        
        if TempStack:
            TempStack.reverse()
            Stack.extend(TempStack)
        
        # At this moment, RE has already been transformed to stacks!

        self.FAStack = list()
        FACounter = 0

        # Thompson's construction
        # pop element from stack, create a finite automata for it, then
        # push the FA to the stack
        for Type, Value, Level in Stack:
            if rule.CheckIsOp(Type):
                if Type == 'CLOSURE':
                    # closure only needs one operand, so only one pop()
                    # performed
                    fa = self.FAStack.pop()
                    fa.CreateClosure()
                    self.FAStack.append(fa)

                elif Type == 'CONCATENATION':
                    # concatenation requires two operand, so two pop()
                    # performed
                    fa = self.FAStack.pop()

                    # the FA passed toCreateConcatenation will be attached
                    # after this FA
                    fa.CreateConcatenation(self.FAStack.pop())
                    self.FAStack.append(fa)

                elif Type == 'ALTERNATION':
                    fa = self.FAStack.pop()
                    fa.CreateAlternation(self.FAStack.pop())
                    self.FAStack.append(fa)

                else:
                    # There should not be any other type of operators in
                    # the stack
                    print 'Wrong operator type.'
                    assert False
            else:
                # It's a char. create a NFA for this char
                fa = FA.FiniteAutomata(FACounter, Value)
                self.FAStack.append(fa)
                FACounter += 1
        
        assert len(self.FAStack) == 1
        self.NFA = self.FAStack.pop()
    

    def NFAtoDFA(self):
        """This function transforms a NFA to deterministic
        finite automata (DFA) by using Subset Construction
        """
        q0 = self.NFA.FindEpsilonClosure(self.NFA.GetStartState().pop())
        Q = [q0,]
        WorkList = [q0,]
        SetCounter = 0
        WorkListIndex = [SetCounter,]

        self.TransitionMap = dict()
        self.StartStates = [0,]
        self.AcceptStates = list()

        while len(WorkList) > 0:

            q = WorkList.pop()
            idx = WorkListIndex.pop()

            for state in q:
                if state in self.NFA.GetAcceptState():
                    self.AcceptStates.append(idx)
                    break

            for char in rule.ForAllChar():
                # t <- e-closure(Delta(q, c))
                t = self.NFA.FindTransitionList(q, char)
                if len(t) == 0:
                    continue
                t = self.NFA.FindEpsilonClosureList(t)

                # if t not in Q then
                #     add t to Q and WorkList
                if t not in Q:
                    SetCounter += 1
                    Q.append(t)
                    WorkList.append(t)
                    WorkListIndex.append(SetCounter)
                
                # T[q, c] <- t
                key = str(idx) + '_' + char
                self.TransitionMap[key] = Q.index(t)
        
        self.NumStates = SetCounter
            
        # for key in self.TransitionMap.keys():
        #     print key, '=>',
        #     print self.TransitionMap[key]
        # print 'Accept =', self.AcceptStates
    
    def MinimizeDFA(self, ):
        """This function minimizes the number of states of
        a given DFA by using Hopcroft's Algorithm."""

        def Split(S):
            """This function split a given set according to their
            reaction to input characters."""
            # for each char do
            #     if c splits S into s1 and s2
            #         then return {s1, s2}
            
            # return S

        # T <- {Da, {D - Da}}
        # P <- {}

        T = [[ID for ID in range(self.NumStates + 1) if ID not in self.AcceptStates],
            self.AcceptStates]
        Set1 = [ID for ID in range(self.NumStates + 1) if ID not in self.AcceptStates]
        if Set1:
            T = [Set1, self.AcceptStates]
        else:
            T = [self.AcceptStates]
        P = list()

        # Minimize DFA using the following algorithm:
        # 
        # while P != T do
        #     P <- T
        #     T <- {}
        #     for each set p in P do
        #         T <- T | Split(p)
        __counter = 0
        while len(P) != len(T):
            if __counter > 10:
                print "ERROR: loop forever"
                exit()
            __counter += 1
            
            P = T[:]
            T = list()
            for p in P:
                if len(p) == 1:
                    # p has only one member, nothing to split
                    T.append(p)
                    continue
                # p should not be empty
                assert p

                s1 = list()
                s2 = list()
                # main splitting function
                for idx, char in enumerate(rule.ForAllChar()):
                    for state in p:
                        # state should be a string
                        key = str(state) + '_' + char
                        if key in self.TransitionMap:
                            if self.TransitionMap[key] not in p:
                                s2.append(state)
                            else:
                                s1.append(state)
                        else:
                            s2.append(state)
                    
                    if s2 and s1:
                        # set splitted. exit the loop to update the main list
                        break
                    elif idx < len(rule.ForAllChar()) - 1:
                        # clear s1 and s2, enter the next round
                        del s1[:]
                        del s2[:]

                if not s2 or not s1:
                    # the set is not splitted, so just append p
                    T.append(p)
                else:
                    # set is splitted into s1 and s2
                    T.append(s1)
                    T.append(s2)

        # Now, create a new Transition Map
        NewTransitionMap = dict()
        for States in T:
            for char in rule.ForAllChar():
                key = str(States[0]) + '_' + char
                if key in self.TransitionMap:
                    # Cannot directly copy the destination state, because they
                    # already have new ids. have to use the new state id here
                    for states in T:
                        if self.TransitionMap[key] in states:
                            # doesn't matter which id in the set is used, since
                            # they all have the same behavior
                            # choose first state here
                            NewTransitionMap[key] = states[0]
        
        self.TransitionMap = dict(NewTransitionMap.items())
        
        # Modify the accepting State
        NewAcceptStates = set()
        for States in T:
            for state in States:
                if state in self.AcceptStates:
                    NewAcceptStates.add(States[0])
                    break
        self.AcceptStates = list(NewAcceptStates)
        
        # Modify the starting State
        NewStartStates = set()
        for States in T:
            for state in States:
                if state in self.StartStates:
                    NewStartStates.add(States[0])
                    break
        self.StartStates = list(NewStartStates)

        # for key, value in self.TransitionMap.items():
        #     print key, '=>', value
        # print 'Accept =', self.AcceptStates
        # print 'Start =', self.StartStates
    
    def Match(self, Str, Greedy=True):
        LastMatch = -1
        state = self.StartStates[0]
        for idx, char in enumerate(Str):
            key = str(state) + '_' + char
            if key in self.TransitionMap:
                state = self.TransitionMap[key]
                if state in self.AcceptStates:
                    if Greedy:
                        LastMatch = idx
                    else:
                        return idx
            else:
                return LastMatch
        return LastMatch

    
    def DFAtoRE(self):
        """This function transforms a given DFA into a
        regular expression using Kleene's construction."""

        pass

if __name__ == '__main__':
    # re = '\\[\\*nad[b-eACD-]+[4-1]'
    # re = '(ab*|ba)*a'
    # re = '[a-c]+'
    re = 'aa(a|b|c)'
    # re = '(ab|aaa)bbba'
    # re = 'a*'
    # re = 'aba|ab'
    # re = '*a'
    # re = ''
    # re = '((()))'

    parser = Parser(re)

    string = 'aaaaaaa'

    print 'Position where string', string, 'is matched by re', re, ':',
    # print parser.Match(string, False)
    pos = parser.Match(string, True)
    print pos
    print string
    print ' ' * pos + '^'