# File Name : rule.py
# Description : This file specifies the rule implemented in
#     this parser.

TYPES = ['OPERATOR', 'DIGIT', 'LETTER', 'CHARACTER']

OPERATOR = dict({'|' : 'ALTERNATION',
                 'CON' : 'CONCATENATION',
                 '*' : 'CLOSURE',
                 '+' : 'AT_LEAST_ONE',
                 '[' : 'LEFT_SQUARE_BRACKET',
                 ']' : 'RIGHT_SQUARE_BRACKET',
                 '-' : 'DASH',
                 '(' : 'LEFT_PARENTHESES',
                 ')' : 'RIGHT_PARENTHESES'})

# precedence of basic operators: the operator with smaller
# index has higher precedence.
PRECEDENCE = ['CLOSURE', 'CONCATENATION', 'ALTERNATION', None]

DIGIT = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

LETTER_LOWER = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
                'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                'y', 'z']

LETTER_UPPER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                'Y', 'Z']

CHARACTER = dict({
            # those don't need escaping
            ',' : ',',
            '.' : '.',
            '/' : '/',
            '{' : '{',
            '}' : '}',
            '!' : '!',
            '@' : '@',
            '#' : '#',
            '$' : '$',
            '%' : '%',
            '^' : '^',
            '&' : '&',
            '<' : '<',
            '>' : '>',
            ':' : ':',
            ';' : ';',
            "'" : "'",
            '"' : '',
            '~' : '',
            '`' : '',
            '_' : '',
            # those need escaping
            "\s" : ' ',
            "\\\\" : "\\",
            "\\n" : '\n',
            "\\t" : '\t',
            "\\[" : '[',
            "\\]" : ']',
            "\\+" : '+',
            "\\-" : '-',
            "\\*" : '*',
            "\\|" : '|',
            "\\(" : '(',
            "\\)" : ')',
            "EPSILON" : "EPSILON"})

ALLCHARS = DIGIT + LETTER_LOWER + LETTER_UPPER + \
[char for char in CHARACTER.values() if char != 'EPSILON']

def ForAllChar():
    # Should not include EPSILON!
    # return DIGIT + LETTER_LOWER + LETTER_UPPER + CHARACTER.values()
    return ALLCHARS
    # return ['a', 'b']

def CheckCharType(char):
    """Find out what kind of character is this."""
    # char should be a character
    # if len(char) > 2:
    #     return None
    if char in OPERATOR:
        return OPERATOR[char], char
    elif char in DIGIT:
        return 'DIGIT', char
    elif char in LETTER_LOWER or char in LETTER_UPPER:
        return 'LETTER', char
    elif char in CHARACTER:
        return 'CHARACTER', CHARACTER[char]
    else:
        # Not Found
        return None, None

def CheckIsOp(Type):
    if Type == 'ALTERNATION' or Type == 'CONCATENATION' or Type == 'CLOSURE':
        return True
    elif Type == 'LEFT_PARENTHESES' or Type == 'RIGHT_PARENTHESES':
        return False
    else:
        return False

def CheckIsChar(Type):
    """Return Boolean value which indicates whether the
    character given is an operator."""

    if Type == 'ALTERNATION' or Type == 'CONCATENATION' or Type == 'CLOSURE':
        return False
    elif Type == 'LEFT_PARENTHESES' or Type == 'RIGHT_PARENTHESES':
        return False
    else:
        return True

def CheckIsOneOprandOp(Type):
    if Type == 'CLOSURE' or Type == 'AT_LEAST_ONE':
        return True
    else:
        return False

# def __TestCheckCharType():
#     print '\\+ is', CheckCharType('\\+')
#     print 'n is', CheckCharType('n')
#     print '0 is', CheckCharType('0')
#     print '+ is', CheckCharType('+')

def CheckPrecedenceHigherThan(OP1, OP2):
    """This function compares the precedence of the two
    given operators, if the first operator has higher
    precedence it returns true. It returns false
    otherwise."""

    if OP1 not in PRECEDENCE or OP2 not in PRECEDENCE:
        # should report error here
        print 'TYPE ERROR: only basic operators are',
        print 'allowed in CheckPrecedenceHigherThan'
        exit()
    
    if PRECEDENCE.index(OP1) < PRECEDENCE.index(OP2):
        return True
    
    return False

def CheckPrecedenceLessThan(OP1, OP2):
    """This function compares the precedence of the two
    given operators, if the first operator has higher
    precedence it returns true. It returns false
    otherwise."""

    if OP1 not in PRECEDENCE or OP2 not in PRECEDENCE:
        # should report error here
        print 'TYPE ERROR: only basic operators are',
        print 'allowed in CheckPrecedenceHigherThan'
        exit()
    
    if PRECEDENCE.index(OP1) > PRECEDENCE.index(OP2):
        return True
    
    return False

# def __TestCheckPrecedenceHigherThan():
#     # True
#     for OP1 in PRECEDENCE:
#         for OP2 in PRECEDENCE:
#             print OP1, 'has higher precedence than', OP2, ':',
#             print CheckPrecedenceHigherThan(OP1, OP2)

def CheckConcatenation(ThisType, LastType, IsInBracket):
    """check if an concatenation should be added between
    this character and the last character"""

    # there is only alternations inside brackets
    if IsInBracket:
        return False
    
    if ThisType in ['DIGIT', 'LETTER', 'CHARACTER',
                    'LEFT_SQUARE_BRACKET',
                    'LEFT_PARENTHESES']:
        if LastType in ['DIGIT', 'LETTER', 'CHARACTER',
                        'CLOSURE', 'AT_LEAST_ONE',
                        'RIGHT_SQUARE_BRACKET', 
                        'RIGHT_PARENTHESES']:
            return True

    return False

def IsValidDashOperand(Char):
    """Check if the given character is allowed to
    appear in a dash expression."""
    
    if Char in DIGIT:
        Val = True
    elif Char in LETTER_LOWER:
        Val = True
    elif Char in LETTER_UPPER:
        Val = True
    else:
        Val = False
    return Val

# def __TestIsValidDashMember():
#     print IsValidDashOperand('a')
#     print IsValidDashOperand('A')
#     print IsValidDashOperand('8')
#     print IsValidDashOperand('[')

def ConvertDashExpression(FirstChar, LastChar):
    """This function converts the dash expression (for
    example, A-Z, a-z, 0-9) to lists of characters."""
    # Should I use string.ascii_letters instead?

    # print '\'', FirstChar, '\' to \'', LastChar, '\''

    if FirstChar in DIGIT and LastChar in DIGIT:
        IndexHigh = max([DIGIT.index(FirstChar),
                        DIGIT.index(LastChar)])
        IndexLow = min([DIGIT.index(FirstChar),
                       DIGIT.index(LastChar)])
        return zip(['DIGIT'] * (IndexHigh - IndexLow + 1),
                   DIGIT[IndexLow : IndexHigh + 1])
                       
    elif FirstChar in LETTER_LOWER and LastChar in LETTER_LOWER:
        IndexHigh = max([LETTER_LOWER.index(FirstChar),
                        LETTER_LOWER.index(LastChar)])
        IndexLow = min([LETTER_LOWER.index(FirstChar),
                       LETTER_LOWER.index(LastChar)])
        return zip(['LETTER'] * (IndexHigh - IndexLow + 1),
                   LETTER_LOWER[IndexLow : IndexHigh + 1])

    elif FirstChar in LETTER_UPPER and LastChar in LETTER_UPPER:
        IndexHigh = max([LETTER_UPPER.index(FirstChar),
                        LETTER_UPPER.index(LastChar)])
        IndexLow = min([LETTER_UPPER.index(FirstChar),
                       LETTER_UPPER.index(LastChar)])
        return zip(['LETTER'] * (IndexHigh - IndexLow + 1),
                   LETTER_UPPER[IndexLow : IndexHigh + 1])
    else:
        return list()

# def __TestConvertDashExpression():
#     # reverse order
#     print '7-1 =>', ConvertDashExpression('7', '1')
#     # letter in lower case
#     print 'a-t =>', ConvertDashExpression('a', 't')
#     # upper case
#     print 'D-G =>', ConvertDashExpression('D', 'G')
#     # letter in different case (should return None)
#     print 'a-A =>', ConvertDashExpression('a', 'A')

#     print 'a-a =>', ConvertDashExpression('a', 'a')

def __FindDuplicate(List):
    """heck if there is duplicate in CHARACTER"""
    for char in List:
        if len([ch for ch in CHARACTER if ch == char]) > 1:
            print 'Duplicate! ('+char+')'

if __name__ == '__main__':
    __FindDuplicate(ForAllChar())
    # __FindDuplicate(CHARACTER)
    # __TestCheckCharType()
    # __TestIsValidDashMember()
    # __TestConvertDashExpression()
    # __TestCheckPrecedenceHigherThan()
