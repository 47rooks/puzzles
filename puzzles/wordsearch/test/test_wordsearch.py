'''
Created on Mar 19, 2017

@author: Daniel
'''
import unittest
from bibleutils.versification import convert_refs, expand_refs, parse_refs, \
                                     ReferenceFormID
from puzzles.core.etcbc import Corpus, get_words
from puzzles.wordsearch.wordsearch import WordSearch

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGreekWordsearch(self):
        refs = expand_refs(convert_refs(parse_refs('Luke 1:2,5', form='ETCBCG'),
                           ReferenceFormID.ETCBCG))
        
        # Get the list of words from TF
        sections = []
        [sections.append((r.st_book, r.st_ch, r.st_vs)) for r in refs ]
        word_list = get_words(*sections, work=Corpus.GREEK)

        ws = WordSearch(set(word_list), 10, 10, WordSearch.LTR)
        ws.dump('html')
        
        # Verify results
        # Due to randomization of direction in the layout it is impossible to
        # simply verify the layout. For now check only the number of words and
        # approximate grid size
        self.assertEqual(len(ws._words), 37, 'Incorrect number of words')
        self.assertGreater(ws._right, 10, 'right extent too small')
        self.assertLess(ws._right, 16, 'right extent too large')
        self.assertGreater(ws._bottom, 12, 'bottom extent too small')
        self.assertLess(ws._bottom, 16, 'bottom extent too large')

    def testHebrewWordsearch(self):
        refs = expand_refs(convert_refs(parse_refs('Genesis 1:5', form='ETCBCH'),
                           ReferenceFormID.ETCBCH))
        
        # Get the list of words from TF
        sections = []
        [sections.append((r.st_book, r.st_ch, r.st_vs)) for r in refs ]
        word_list = get_words(*sections, work=Corpus.HEBREW)
 
        ws = WordSearch(set(word_list), 10, 10, WordSearch.RTL)
        ws.dump('html')
           
        self.assertEqual(len(ws._words), 18, 'Incorrect number of words')
        self.assertGreater(ws._left, -10, 'left extent too small')
        self.assertLess(ws._left, -5, 'left extent too large')
        self.assertGreater(ws._bottom, 5, 'bottom extent too small')
        self.assertLess(ws._bottom, 9, 'bottom extent too large')

    def testHebrewWordsearchMultiChapter(self):
        refs = expand_refs(convert_refs(parse_refs('Genesis 1:5, Exodus 1:2',
                                                   form='ETCBCH'),
                           ReferenceFormID.ETCBCH))
        
        # Get the list of words from TF
        sections = []
        [sections.append((r.st_book, r.st_ch, r.st_vs)) for r in refs ]
        word_list = get_words(*sections, work=Corpus.HEBREW)
 
        ws = WordSearch(set(word_list), 10, 10, WordSearch.RTL)
        ws.dump('html')
           
        self.assertEqual(len(ws._words), 23, 'Incorrect number of words')
        self.assertGreater(ws._left, -10, 'left extent too small')
        self.assertLess(ws._left, -5, 'left extent too large')
        self.assertGreater(ws._bottom, 5, 'bottom extent too small')
        self.assertLess(ws._bottom, 10, 'bottom extent too large')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()