# File Name : parser.py
# Description : This file implements the main parser
#     functionality.
from FA import State
from FA import FiniteAutomata
from rule import CheckCharType
from rule import CheckConcatenation
from rule import ConvertDashExpression
from rule import IsValidDashOperand
from rule import CheckIsOp
from rule import CheckIsChar
from rule import CheckPrecedenceHigherThan
from rule import CheckPrecedenceLessThan
from rule import CheckIsOneOprandOp
from rule import ForAllChar


class Parser:
    """This is the parser class. It implements the main
    functionality"""

    def __init__(self, exp=None):
        """This function implements the initialization
        process of the parser class."""
        if type(exp) is str and len(exp) is not 0:
            self.DefineRE(exp)
            self.REtoNFA()
            self.NFAtoDFA()
        else:
            # should raise exception
            pass
        
    def ScanRE(self, exp):
        """Used to parse the regular expression into an
        intermediate representation."""
        # Make sure the expression is not empty
        if type(exp) is not str:
            return
        
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
            
            self.NotedRE.append(CheckCharType(ch))


    def DefineRE(self, exp):
        """This function take the regular expression as input,
        and transforms it internally."""

        # Clean old RE and its DFA (if it exist)
        try:
            del self.FA
        except AttributeError:
            pass

        # process the new RE
        self.Stack = list()
        # should tell the user if there's error
        self.ScanRE(exp)
    
    def REtoNFA(self):
        """This function transforms a regular expression to
        a non-deterministic finite automata (NFA) using the
        method "Thompson's Construction"."""

        def AddConcatToNotedRE(NotedRE):
            """concatenations are not denoted explicitly
            in the original regular expression, so we
            add them to the RE in here."""

            if len(NotedRE) == 0:
                return
            
            ModifiedRE = list()
            LastType = None
            for idx, (Type, Value) in enumerate(NotedRE):
                if LastType == 'LEFT_SQUARE_BRACKET':
                    InBracket = True
                elif LastType == 'RIGHT_SQUARE_BRACKET':
                    InBracket = False
                elif LastType is None:
                    InBracket = False
                if idx > 0 and CheckConcatenation(Type,
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
                        Test2 = IsValidDashOperand(Value)
                        Test3 = idx == len(NotedRE) - 1
                        if Test3 and Test2:
                            ModifiedRE.append(('ALTERNATION', '|'))
                            ModifiedRE.append((Type, Value))
                        elif NotedRE[idx + 1][0] != 'DASH' and Test2:
                            if idx > 0:
                                ModifiedRE.append(('ALTERNATION', '|'))
                            ModifiedRE.append((Type, Value))
                elif FlagDash and IsValidDashOperand(Value):
                    CharTo = Value
                    # if PosFrom > 0:
                    #     print '1'
                    #     ModifiedRE.append(('ALTERNATION', '|'))
                    for idx, (Type, Value) in enumerate(ConvertDashExpression(CharFrom,
                                                             CharTo)):
                        if idx > 0 or PosFrom > 0:
                            ModifiedRE.append(('ALTERNATION', '|'))
                        ModifiedRE.append((Type, Value))
                    FlagDash = False
            
            return ModifiedRE[:]
            # pass

        def AddAlterToNotedRE(NotedRE):
            """Since alternations are already specified
            explicitly in the regular expression, all
            this function does is to change things inside
            brackets to a string of alternations."""

            if len(NotedRE) == 0:
                return
            
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
                        if IsValidDashOperand(Value) or Type == 'DASH':
                            REToTransform.append((Type, Value))
                
                LastType = Type
            return ModifiedRE[:]
        
        def FindLastOpBeforePos(NotedRE, Pos):
            """This function find the position of the
            last operand before the given position"""

            if len(NotedRE) == 0:
                # TODO: tell the user about the error
                return
            Count = 0
            for i in range(Pos - 1, -1, -1):
                if NotedRE[i][0] is 'RIGHT_PARENTHESES':
                    Count += 1
                elif NotedRE[i][0] is 'LEFT_PARENTHESES':
                    Count -= 1
                if Count == 0:
                    return i


        def ConvertToSimpleRE(NotedRE):
            """This function transforms special
            operators to a combination of simple
            operators ('|', '*', concatenation)"""

            if len(NotedRE) == 0:
                # TODO: tell the user about the error
                return
            
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
            	# 	print 'ERROR!'
            	# 	exit()
            	# __counter += 1
                if LastRE[idx][0] == 'AT_LEAST_ONE':
                    # find its operand
                    if idx == 0:
                        # should raise an error here
                        return
                    else:
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
            # print Type,

            try:
                # print TempStack[-1][0],
                PrecHigherThan = CheckPrecedenceHigherThan(Type, TempStack[-1][0])
                PrecLessThan = CheckPrecedenceLessThan(Type, TempStack[-1][0])
                SameLevel = Level == TempStack[-1][2]
            except IndexError:
                # print 'None',
                PrecHigherThan = CheckPrecedenceHigherThan(Type, None)
                PrecLessThan = CheckPrecedenceLessThan(Type, None)
                SameLevel = False
            
            return PrecHigherThan, PrecLessThan, SameLevel
        
        # REtoNFA finally starts here...

        # should check if NotedRE exist
        if len(self.NotedRE) == 0:
            return
        
        self.NotedRE = AddConcatToNotedRE(self.NotedRE)
        self.NotedRE = AddAlterToNotedRE(self.NotedRE)
        self.NotedRE = ConvertToSimpleRE(self.NotedRE)
        Stack = list()
        TempStack = list()
        Level = 0
        for Type, Value in self.NotedRE:
            if CheckIsChar(Type):
                # Chars are put into the stack directly
                Stack.append((Type, Value, Level))
            elif Type == 'LEFT_PARENTHESES':
                # Enter the next level
                Level += 1
            elif Type == 'RIGHT_PARENTHESES':
                # all operator has to be put into the stack before we leave
                # this level
                if len(TempStack) > 0:
                    if TempStack[-1][2] == Level:
                        while True:
                            Stack.append(TempStack.pop())
                            if len(TempStack) == 0 or TempStack[-1][2] != Level:
                                break

                Level -= 1
            elif CheckIsOp(Type):
                
                while True:
                    PrecHigherThan, PrecLessThan, SameLevel = CheckPrec(Type, Level, TempStack)
                    
                    # operators like closure should be put into stack directly
                    # since they are associated with one operand only, so we don't
                    # have to consider their precedence
                    if CheckIsOneOprandOp(Type):
                        Stack.append((Type, Value, Level))
                        break

                    # otherwise, we can push the previous operator in the stack, but
                    # still can't push the current operator into the stack
                    elif PrecHigherThan and SameLevel:
                        # print '>'
                        # Stack.append(TempStack.pop())
                        TempStack.append((Type, Value, Level))
                        break
                    
                    elif PrecLessThan and SameLevel:
                        # print '<'
                        Stack.append(TempStack.pop())
                    
                    elif not PrecLessThan and not PrecHigherThan and SameLevel:
                        # print '='
                        Stack.append(TempStack.pop())
                        TempStack.append((Type, Value, Level))
                        break
                    
                    # if the current operator has higher precedence than the one in
                    # the previous one, than we can't put the operator in the stack
                    # yet since the other operator has not shown up
                    else:
                        # print '!'
                        TempStack.append((Type, Value, Level))
                        break

            else:
                # Error!
                print 'ERROR: unknown char type.'
        
        if len(TempStack) > 0:
            TempStack.reverse()
            Stack.extend(TempStack)
        
        # At this moment, RE has already been transformed to stacks!
        
        # for Type, Value, Level in Stack:
        #     print Value,

        self.FAStack = list()
        FACounter = 0

        for Type, Value, Level in Stack:
            if CheckIsOp(Type):
                if Type == 'CLOSURE':
                    fa = self.FAStack.pop()
                    fa.CreateClosure()
                    self.FAStack.append(fa)
                elif Type == 'CONCATENATION':
                    fa = self.FAStack.pop()
                    fa.CreateConcatenation(self.FAStack.pop())
                    self.FAStack.append(fa)
                elif Type == 'ALTERNATION':
                    fa = self.FAStack.pop()
                    fa.CreateAlternation(self.FAStack.pop())
                    self.FAStack.append(fa)
                else:
                    pass
            else:
                # It's a char. create a NFA for this char
                fa = FiniteAutomata(FACounter, Value)
                self.FAStack.append(fa)
                FACounter += 1
        
        if len(self.FAStack) != 1:
            print 'More than one FA left in the stack!'
            pass
        
        self.NFA = self.FAStack.pop()
        # self.NFA.Print()

        # return fa
    
    def NFAtoDFA(self):
        """This function transforms a NFA to deterministic
        finite automata (DFA) by using Subset Construction
        """
        q0 = self.NFA.FindEpsilonClosure(self.NFA.GetStartState().pop())

        for state in self.NFA.States:
            print state.ID,
        print ''
        Q = [q0,]
        WorkList = [q0,]
        SetCounter = 0
        WorkListIndex = [SetCounter,]

        self.TransitionMap = dict()
        self.StartStates = [0,]
        self.AcceptStates = list()

        __counter = 0

        while len(WorkList) > 0:
            if __counter > 1000:
                print 'ERROR!!'
                exit()
            __counter += 1

            q = WorkList.pop()
            idx = WorkListIndex.pop()

            for state in q:
                # print state, self.NFA.GetAcceptState()
                if state in self.NFA.GetAcceptState():
                    self.AcceptStates.append(idx)
                    break

            for char in ForAllChar():
                # t <- e-closure(Delta(q, c))
                
                t = self.NFA.FindTransitionList(q, char)
                if len(t) == 0:
                    continue
                print q, t,
                t = self.NFA.FindEpsilonClosureList(t)
                print t

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
            
        for key in self.TransitionMap.keys():
            print key, '=>',
            print self.TransitionMap[key]
        print self.AcceptStates
        # print Q
    
    def MinimizeDFA(self, ):
        """This function minimizes the number of states of
        a given DFA by using Hopcroft's Algorithm."""
        pass
    
    def DFAtoRE(self, ):
        """This function transforms a given DFA into a
        regular expression using Kleene's construction."""

        pass

if __name__ == '__main__':
    # re = '\\[\\*nad[b-eACD-]+[4-1]'
    re = '(ab*|ba)*a'
    # re = 'aba|ab'
    parser = Parser(re)
    # print ConvertDashExpression('7', '1')
    