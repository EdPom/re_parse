# File Name: FA_test.py
# Description: This file implements the unit test class for class FA

import unittest
import FA

class test_FA(unittest.TestCase):
    def setUp(self):
        """Initialization before the actual tests"""
        self.fa = FA.FiniteAutomata(0, 'a')
    
    def test_FAInit(self):
        """Create a FA instance"""
        NewFA = FA.FiniteAutomata(0, 'b')
        self.assertTrue(NewFA)
    
    def test_AddState(self):
        """Add 5 states into the FA"""
        for i in range(5):
            val = self.fa.AddState()
            self.assertTrue(val > 0)
    
    def test_FindStatePosByID(self):
        ValidID = self.fa.States[-1].ID
        val = self.fa.FindStatePosByID(ValidID)
        self.assertTrue(val >= 0)

        VeryBigID = '99999999'
        val = self.fa.FindStatePosByID(VeryBigID)
        self.assertEqual(val, -1)

    # Question: How do I test closure creation and epsilon closure?

if __name__ == '__main__':
    unittest.main()