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
            "\\)" : ')'})

def CheckCharType(char):
    """Find out what kind of character is this."""
    # char should be a character
    if len(char) > 2:
        return None
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

def __TestCheckCharType():
    print '\\+ is', CheckCharType('\\+')
    print 'n is', CheckCharType('n')
    print '0 is', CheckCharType('0')
    print '+ is', CheckCharType('+')

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

def __TestIsValidDashMember():
    print IsValidDashOperand('a')
    print IsValidDashOperand('A')
    print IsValidDashOperand('8')
    print IsValidDashOperand('[')

def ConvertDashExpression(FirstChar, LastChar):
    """This function converts the dash expression (for
    example, A-Z, a-z, 0-9) to lists of characters."""

    # print '\'', FirstChar, '\' to \'', LastChar, '\''

    if FirstChar in DIGIT:
        if LastChar not in DIGIT:
            return
        else:
            IndexHigh = max([DIGIT.index(FirstChar),
                            DIGIT.index(LastChar)])
            IndexLow = min([DIGIT.index(FirstChar),
                           DIGIT.index(LastChar)])
            return zip(['DIGIT'] * (IndexHigh - IndexLow + 1),
                       DIGIT[IndexLow : IndexHigh + 1])
                       
    elif FirstChar in LETTER_LOWER:
        if LastChar not in LETTER_LOWER:
            return
        else:
            IndexHigh = max([LETTER_LOWER.index(FirstChar),
                            LETTER_LOWER.index(LastChar)])
            IndexLow = min([LETTER_LOWER.index(FirstChar),
                           LETTER_LOWER.index(LastChar)])
            return zip(['LETTER'] * (IndexHigh - IndexLow + 1),
                       LETTER_LOWER[IndexLow : IndexHigh + 1])
    elif FirstChar in LETTER_UPPER:
        if LastChar not in LETTER_UPPER:
            return
        else:
            IndexHigh = max([LETTER_UPPER.index(FirstChar),
                            LETTER_UPPER.index(LastChar)])
            IndexLow = min([LETTER_UPPER.index(FirstChar),
                           LETTER_UPPER.index(LastChar)])
            return zip(['LETTER'] * (IndexHigh - IndexLow + 1),
                       LETTER_UPPER[IndexLow : IndexHigh + 1])
    
    return list()

def __TestConvertDashExpression():
    # reverse order
    print '7-1 =>', ConvertDashExpression('7', '1')
    # letter in lower case
    print 'a-t =>', ConvertDashExpression('a', 't')
    # upper case
    print 'D-G =>', ConvertDashExpression('D', 'G')
    # letter in different case (should return None)
    print 'a-A =>', ConvertDashExpression('a', 'A')

def __FindDuplicate(List):
    """heck if there is duplicate in CHARACTER"""
    for char in List:
        if len([ch for ch in CHARACTER if ch == char]) > 1:
            print 'Duplicate! ('+char+')'

if __name__ == '__main__':
    # __FindDuplicate(CHARACTER)
    # __TestCheckCharType()
    # __TestIsValidDashMember()
    __TestConvertDashExpression()
