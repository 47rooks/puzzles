'''
Created on Jan 18, 2017

@author: Daniel
'''

from tf.fabric import Fabric
from bibleutils.versification import Identifier
from inspect import currentframe
import gc

class __Corpus(Identifier):
    '''Defines the corpus identifiers. Essentially this is just Hebrew or Greek
    right.
    '''
    # FIXME would like to distinguish work and corpus eventually but not 
    # necessary now.

    def __init__(self):
        super().__init__({'GREEK' : 1,
                          'HEBREW' : 2})
 
    @property
    def GREEK(self):
        return self._map.get(currentframe().f_code.co_name)
    
    @property
    def HEBREW(self):
        return self._map.get(currentframe().f_code.co_name)

Corpus = __Corpus()

def get_words(*refs, work=Corpus.HEBREW):
    '''
    Get a list of unique words in the specified work, book, chapter and verses.
    
    Parameters
        refs is a list of tuples, each tuple being book, chapter and verse. 
            books are string names as defined in Text-Fabric for English.
            chapter and verse are integers.
    '''
    
    if work == Corpus.HEBREW:
        work_home = 'hebrew/etcbc4c'
        word_feature = 'g_word_utf8'
    elif work == Corpus.GREEK:
        work_home = 'greek/sblgnt'
        word_feature = 'g_word'
        
    TF = Fabric(modules=[work_home], silent=True)
    api = TF.load(word_feature, silent=True)
    lex_list = []
    for ref in refs:
        verse_nodes = api.T.nodeFromSection(ref)
        slots = api.L.d(verse_nodes, 'word')
        lex_list.extend([api.Fs(word_feature).v(s) for s in slots])
        
    # GC the TF layer
    TF = None
    api = None
    gc.collect(0)
    gc.collect(1)
    gc.collect(2)
    
    return lex_list
