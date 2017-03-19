'''
Created on Feb 5, 2017

@author: Daniel
'''
import unittest
from puzzles.core.etcbc import get_words
from puzzles.core.etcbc import Corpus

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    #def testTF(self):
    #    ETCBC = 'hebrew/etcbc4c'
    #    PHONO = 'hebrew/phono'
    #    TF = Fabric( modules=[ETCBC, PHONO] )

    #    api = TF.load('''
    #        sp lex voc_utf8
    #        g_word trailer
    #        qere qere_trailer
    #        language freq_lex gloss
    #        mother
    #    ''')
    
    #    api.makeAvailableIn(globals())

    def testGetHebrewWords(self):
        l = get_words(('Genesis', 1, 1),('Genesis', 1, 2),('Genesis', 1, 3))
        print(f'Got {len(l)} words : {l}')
   
    def testGetGreekWords(self):
        l = get_words(('Matthew', 1, 1),('Matthew', 1, 2),('Matthew', 1, 3),
                       work=Corpus.GREEK)
        print(f'Got {len(l)} words : {l}')
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()