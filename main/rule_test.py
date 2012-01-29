# File Name: rule_test.py
# Description:This file tests all functions in rule.py

import unittest
import rule

class test_RuleFunction(unittest.TestCase):
    def test_CheckCharType(self):
        for char in rule.OPERATOR.keys():
            Type, Value = rule.CheckCharType(char)
            self.assertEqual(Type, rule.OPERATOR[char])
        for char in rule.DIGIT:
            Type, Value = rule.CheckCharType(char)
            self.assertEqual(Type, 'DIGIT')
        for char in rule.LETTER_LOWER + rule.LETTER_UPPER:
            Type, Value = rule.CheckCharType(char)
            self.assertEqual(Type, 'LETTER')
        for char in rule.CHARACTER:
            Type, Value = rule.CheckCharType(char)
            self.assertEqual(Type, 'CHARACTER')
    
    def test_CheckPrecedenceHigherThan(self):
        for id1, OP1 in enumerate(rule.PRECEDENCE):
            for id2, OP2 in enumerate(rule.PRECEDENCE):
                val = rule.CheckPrecedenceHigherThan(OP1, OP2)
                ans = id1 < id2
                self.assertEqual(val, ans)
    
    def test_CheckPrecedenceLessThan(self):
        for id1, OP1 in enumerate(rule.PRECEDENCE):
            for id2, OP2 in enumerate(rule.PRECEDENCE):
                val = rule.CheckPrecedenceLessThan(OP1, OP2)
                ans = id1 > id2
                self.assertEqual(val, ans)
    
    def test_CheckConcatenation(self):
        pass
    
    def test_ConvertDashExpression(self):
        import string

        # test for lower case leters
        # should be valid
        for id1, char1 in enumerate(string.ascii_lowercase):
            for id2, char2 in enumerate(string.ascii_lowercase):
                val = rule.ConvertDashExpression(char1, char2)
                
                high = max(id1, id2)
                low = min(id1, id2)
                
                ans = zip(['LETTER'] * (high - low + 1),
                          list(string.ascii_lowercase[low:high+1]))
                self.assertEqual(val, ans)
        
        # test for upper case leters
        # should be valid
        for id1, char1 in enumerate(string.ascii_uppercase):
            for id2, char2 in enumerate(string.ascii_uppercase):
                val = rule.ConvertDashExpression(char1, char2)
                
                high = max(id1, id2)
                low = min(id1, id2)
                
                ans = zip(['LETTER'] * (high - low + 1),
                          list(string.ascii_uppercase[low:high+1]))
                self.assertEqual(val, ans)
        
        # test for digits
        # should be valid
        for id1, char1 in enumerate(string.digits):
            for id2, char2 in enumerate(string.digits):
                val = rule.ConvertDashExpression(char1, char2)
                
                high = max(id1, id2)
                low = min(id1, id2)
                
                ans = zip(['DIGIT'] * (high - low + 1),
                          list(string.digits[low:high+1]))
                self.assertEqual(val, ans)
        
        # test for mixture of letters
        # should be invalid
        for id1, char1 in enumerate(string.digits):
            for id2, char2 in enumerate(string.ascii_uppercase):
                val = rule.ConvertDashExpression(char1, char2)
                
                ans = list()
                self.assertEqual(val, ans)

if __name__ == '__main__':
    unittest.main()