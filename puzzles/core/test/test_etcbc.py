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

    def testGetHebrewWords(self):
        l = get_words(('Genesis', 1, 1),('Genesis', 1, 2),('Genesis', 1, 3))
        self.assertEqual(len(l), 39, 'incorrect number of words')
        self.assertEqual(l,
                         ['בְּ', 'רֵאשִׁ֖ית', 'בָּרָ֣א', 'אֱלֹהִ֑ים', 'אֵ֥ת', 'הַ', 'שָּׁמַ֖יִם'
                          , 'וְ', 'אֵ֥ת', 'הָ', 'אָֽרֶץ', 'וְ', 'הָ', 'אָ֗רֶץ', 'הָיְתָ֥ה'
                          , 'תֹ֨הוּ֙', 'וָ', 'בֹ֔הוּ', 'וְ', 'חֹ֖שֶׁךְ', 'עַל', 'פְּנֵ֣י', 'תְהֹ֑ום'
                          , 'וְ', 'ר֣וּחַ', 'אֱלֹהִ֔ים', 'מְרַחֶ֖פֶת', 'עַל', 'פְּנֵ֥י', 'הַ', 'מָּֽיִם'
                          , 'וַ', 'יֹּ֥אמֶר', 'אֱלֹהִ֖ים', 'יְהִ֣י', 'אֹ֑ור', 'וַֽ', 'יְהִי', 'אֹֽור'],
                         'incorrect words retrieved')
   
    def testGetGreekWords(self):
        l = get_words(('Matthew', 1, 1),('Matthew', 1, 2),('Matthew', 1, 3),
                       work=Corpus.GREEK)
        self.assertEqual(len(l), 47, 'incorrect number of words')
        self.assertEqual(l,
                         ['Βίβλος', 'γενέσεως', 'Ἰησοῦ', 'χριστοῦ', 'υἱοῦ',
                          'Δαυὶδ', 'υἱοῦ', 'Ἀβραάμ', 'Ἀβραὰμ', 'ἐγέννησεν',
                          'τὸν', 'Ἰσαάκ', 'δὲ', 'Ἰσαὰκ', 'ἐγέννησεν', 'τὸν',
                          'Ἰακώβ', 'δὲ', 'Ἰακὼβ', 'ἐγέννησεν', 'τὸν', 'Ἰούδαν',
                          'καὶ', 'τοὺς', 'ἀδελφοὺς', 'αὐτοῦ', 'δὲ', 'Ἰούδας',
                          'ἐγέννησεν', 'τὸν', 'Φαρὲς', 'καὶ', 'τὸν', 'Ζάρα',
                          'ἐκ', 'τῆς', 'Θαμάρ', 'δὲ', 'Φαρὲς', 'ἐγέννησεν',
                          'τὸν', 'Ἑσρώμ', 'δὲ', 'Ἑσρὼμ', 'ἐγέννησεν', 'τὸν',
                          'Ἀράμ'],
                         'incorrect words retrieved')
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()