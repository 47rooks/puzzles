#!/usr/local/bin/python2.7
# encoding: utf-8
'''
WordSearch generator command line utility

@author:     47

@copyright:  2017 47Rooks. All rights reserved.

@license:    MIT

@contact:    47rooks@gmail.com
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import json
from random import randrange

from bibleutils.versification import parse_refs, convert_refs, expand_refs,\
     ReferenceFormID
from puzzles.core.etcbc import Corpus, get_words
from uniseg.graphemecluster import grapheme_clusters

__all__ = []
__version__ = 0.1
__date__ = '2017-01-18'
__updated__ = '2017-01-18'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def parse_command_line(args):
    '''Parse command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by 47 on %s.
  Copyright 2017 47Rooks.com. All rights reserved.

  Licensed under the MIT License

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)
        # Add subcommand parsers
        subparsers = parser.add_subparsers(dest='command')
        parser_gen = subparsers.add_parser(
                        'generate',
                        help='generate a wordsearch',
                        formatter_class=RawDescriptionHelpFormatter,
                        epilog='''
Argument Details
                                           
  ETCBCH for the ETCBC Hebrew Old Testament
  ETCBCG for the ETCBC Greek New Testament
  
  VERSES is of the following form and must be in quotes:
    book|book_abbreviation chapter:verse|verse_range
  
    books and book_abbreviations may be obtained with the -b option.
    verse_ranges are of the form:
      
      verse1-verse2
      verse1,verse2,verse17-verse19
      
Example Usages''')
        parser_gen.add_argument("-s", "--scripturerefs", dest="verses",
                             action="store",
                             help="see below [default: first 100 words]")
        parser_gen.add_argument("-c", "--columns", dest="cols",
                             action="store", type=int,
                             help="number of columns in the wordsearch")
        parser_gen.add_argument("-r", "--rows", dest="rows",
                             action="store", type=int,
                             help="number of rows in the wordsearch")
        parser_gen.add_argument("-f", "--format", dest="format",
                             action="store",
                             help="""format of the output,
                             html for HTML output, or
                             fixed for fixed width text output
                             [default: html]""")
        parser_gen.add_argument("text", choices=['ETCBCH', 'ETCBCG'],
                             help="the name of the text. See below")
        
        parser_info = subparsers.add_parser(
                         'info',
                         help='query wordsearch information',
                         formatter_class=RawDescriptionHelpFormatter,
                         epilog='''
Argument Details
                         
  ETCBCH for the ETCBC Hebrew Old Testament
  ETCBCG for the ETCBC Greek New Testament''')
        parser_info.add_argument("text", choices=['ETCBCH', 'ETCBCG'],
                             help="the name of the text. See below")
        parser_info.add_argument("-b", "--books", dest="books",
                            action="store_true",
                            help="""list all books and book_abbreviations for
                            the chosen text. text must be specified but no
                            other options may be specified""")
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    
    # Process arguments
    return parser.parse_args(args)

class WordSearch():
    '''
    Instances of this class hold a grid of letters containing the words
    of the wordsearch, and a list of all the words in the search, which is
    displayed as the clue list.
    
    Parameters
    
    words - a list of source words to put into the wordsearch
    rows - number of rows in grid
    cols - number of columns in grid
    directions - a bit vector of directions to run the words. Ultimately there
    are eight possibilities but only two sets of directions are recognised:
    
        LTR - left to right, top to bottom, left to right diagonal
        RTL - right to left, top to bottom, right to left diagonal
        
        FIXME there is confusion over language direction and the grid directions
              separate these properly
    '''
    LTR = 1
    RTL = 2
    def __init__(self, words, rows, cols, directions):
        # the original inputs to the grid construction
        self._rows = rows
        self._cols = cols
        self._words = words
        
        # the extents of the grid
        self._top = 0
        self._left = 0
        self._right = 0
        self._bottom = 0
        
        # the actual grid
        self._grid = dict()  # tuple (row, col) as key, grapheme as value
        self._placed_words = []

        # Helper variables - try to get rid of these
        self._deepest_row = 0
        if directions == self.LTR:
            self._dirs = ['R','RD','D']
        else:
            self._dirs = ['L','LD','D']
             
        # Statistics
        self._stat_map = dict()
        
        # Generate the grid layout of the word in the word list
        self._generate(directions)
        self._fill_empty_grid_squares()
        
    def _incr_stat(self, stat_name):
        '''Increment a statistic. The name is determined by the caller and 
        may be any string. The counts are literally just integers. The statistic
        will be recorded first on the first call to this function with a value
        of 1. It will be incremented by 1 on each subsequent call.
        
        Parameters
        
        stat_name - the name of the statistic.
        '''
        if self._stat_map.get(stat_name) is None:
            self._stat_map[stat_name] = 1
        else:
            self._stat_map[stat_name] = self._stat_map.get(stat_name) + 1
            
    def _get_sorted_words_list(self):
        '''Generate graphemes for all words and store them in a map
        order the list by the descending number of graphemes.
        '''
        def grapheme_sort(x):
            return len(list(grapheme_clusters(x)))
        graphemes = []
        for w in sorted(self._words,
                        key=grapheme_sort,
                        reverse=True):
            graphemes.append((w, list(grapheme_clusters(w))))
        return graphemes
            
    def _fill_empty_grid_squares(self):
        '''Fill the empty grid squares with random graphemes selected from the
        graphemes in the words in the source word list.
        '''
        graphemes = self._get_sorted_words_list()
        g_list = [g for sublist in list(g_ent[1] for g_ent in graphemes)
                    for g in sublist]
        g_list = list(set(g_list)) # remove duplicates and reform to a list

        for i in range(self._top, self._bottom+1):
            for j in range(self._left, self._right+1):
                sq = (i, j)
                if self._grid.get(sq) is None:
                    self._grid[sq] = g_list[randrange(len(g_list))]

    def _place_word_on_grid(self, g_s, cur_square, cur_dir):
        '''Place graphemes on the grid. Graphemes are placed backward
        along direction from which their placement was checked.
        
        Parameters
        
        g_s the list of graphemes in original text order
        cur_square the last square - where to place the last grapheme
        cur_dir the direction in which the word was placed
        '''
        sq = cur_square
        if cur_dir == 'R':
            if sq[1] > self._right:
                self._right = sq[1]
            for g in reversed(g_s):
                self._grid[sq]=g
                sq = (sq[0], sq[1]-1)
            self._incr_stat('placedR')
        elif cur_dir == 'RD':
            if sq[0] > self._bottom:
                self._bottom = sq[0]
            if sq[1] > self._right:
                self._right = sq[1]
            for g in reversed(g_s):
                self._grid[sq]=g
                sq = (sq[0]-1, sq[1]-1)
            self._incr_stat('placedRD')
        elif cur_dir == 'D':
            if sq[0] > self._bottom:
                self._bottom = sq[0]
            for g in reversed(g_s):
                self._grid[sq]=g
                sq = (sq[0]-1, sq[1])
            self._incr_stat('placedD')
        elif cur_dir == 'L':
            if sq[1] < self._left:
                self._left = sq[1]
            for g in reversed(g_s):
                self._grid[sq]=g
                sq = (sq[0], sq[1]+1)
            self._incr_stat('placedL')
        elif cur_dir == 'LD':
            if sq[0] > self._bottom:
                self._bottom = sq[0]
            if sq[1] < self._left:
                self._left = sq[1]
            for g in reversed(g_s):
                self._grid[sq]=g
                sq = (sq[0]-1, sq[1]+1)
            self._incr_stat('placedLD')
        else:
            raise Exception('unsupported placement direction')

    def _generate(self, lang_direction):
        '''Do the actual generation of the wordsearch
        '''
        graphemes = self._get_sorted_words_list()

        def get_direction(dirs_to_try):
            '''From the provided set of directions select one at random and
            return it. The input set is also modified to leave only unused
            directions in the set.
            FIXME recode to use a closure and thus remove the cross talk via
            the input var side affect.
            '''
            if len(dirs_to_try) == 0:
                return None
            elt = randrange(len(dirs_to_try))
            return dirs_to_try.pop(elt)
        
        def get_starting_square(old):
            # Assumption : the initial 0,0 square is not generated in this
            #              function
            if lang_direction == self.LTR:
                # Start top left go bottom left and arc counter-clockwise to
                # horizontal, step by step. Because it's a grid the arc is
                # a simple right angle.
                if old[0] == self._deepest_row and old[1] != self._deepest_row:
                    return (self._deepest_row, old[1]+1)
                elif old[1] == self._deepest_row and old[0] != 0:
                    return (old[0]-1, old[1])
                elif old[0] == 0 and old[1] == self._deepest_row:
                    self._deepest_row += 1
                    return (self._deepest_row, 0)
                else:
                    raise Exception('LTR row col navigation error')

                if old[1] == 0:
                    self._deepest_row += 1
                    return (self._deepest_row, 0)
                if old[0] == self._deepest_row:
                    return (self._deepest_row, old[1]-1)
                return (old[0] + 1, self._deepest_row)
            
            elif lang_direction == self.RTL:
                # Start top right go bottom right and arc clockwise to
                # horizontal, step by step. Because it's a grid the arc is
                # a simple right angle.
                if old[0] == self._deepest_row and old[1] != -(self._deepest_row):
                    return (self._deepest_row, old[1]-1)
                elif old[1] == -(self._deepest_row) and old[0] != 0:
                    return (old[0]-1, old[1])
                elif old[0] == 0 and old[1] == -(self._deepest_row):
                    self._deepest_row += 1
                    return (self._deepest_row, 0)
                else:
                    raise Exception('RTL row col navigation error')
                
                if old[1] == 0:
                    self._deepest_row += 1
                    return (self._deepest_row, 0)
                if old[0] == self._deepest_row:
                    return (self._deepest_row, old[1]+1)
                return (old[0] + 1, self._deepest_row)
            else:
                raise Exception(f'Invalid lang direction {lang_direction}')
                
        # iterate the list of words to place
        for g_ent in graphemes:
            # This check is required because the code below will not terminate
            # if the grapheme list is empty, which is the case for a zero
            # length word.
            # Now, as a practical matter this does occur with the ETCBC data
            # in the Hebrew, because the slots are allocated with cliticized
            # articles (ה) unpacked into their own slots. However, in the
            # g_* forms these slots are empty, because in the graphical form
            # they are cliticized in vowels on particles and such. So this is
            # really how the data is so this check must remain unless the loops
            # below are altered to handle this, but this check also cuts off
            # more unnecessary code cycles too.
            if g_ent[0] is '': continue

            g_s = g_ent[1]
            # Choose starting square for this attempt to place the word
            #   1. Initial placement square, is top left for LTR and top
            #      right for RTL
            #   2. Next square is a square in the chosen direction
            #      according to the starting square choosing algorithm.
            #      This algorithm chooses squares by radiating out from
            #      the the top left or top right depending upon the
            #      directions parameter, LTR or RTL respectively. Each arc
            #      starts against the 0 column and searches out through the
            #      columns until it reaches the same column number as the
            #      row number and then goes up to the horizontal. The first
            #      square into which the word may be fitted at any direction
            #      is the one chosen. Thus the grid is filled from the top left
            #      or right corner moving out and down as the filling proceeds.
            starting_square = (0, 0)
            self._deepest_row = 0
            starting_squares_available = True
            while starting_squares_available:
                # For a word consider the direction
                #   choose one at random but track which directions have been
                #   attempted. Essentially iterate all three.
                w_placed = False # word not yet placed
                dirs_left = list(self._dirs) # copy the canonical list of dirs
                
                cur_square = starting_square
                cur_dir = get_direction(dirs_left)
                while cur_dir is not None:
                    # Set grapheme counter to zero
                    g_cntr = 0
                    for g in g_s:
                        g_cntr += 1
                        # Attempt placement of the next grapheme in the next
                        # square. It can fit if the square is empty or contains
                        # the same grapheme. All actual placement is deferred
                        # until it is known that the entire word can be placed.
                        # This removes the need for unplacing partial words
                        # on failure.
                        g_placed = False
                        if (self._grid.get(cur_square) is None):
                            g_placed = True
                        elif (self._grid.get(cur_square) == g):
                            # Just note as placed and go on
                            g_placed = True
                        else:
                            # failed to place. Roll back and choose new
                            # starting point
                            pass
                            
                        if g_placed:
                            # If placement succeeds :
                            #   if this is the last grapheme for this word :
                            #      1. mark the word placed
                            #      2. break out of the iterations both grapheme
                            #         and starting location placement.
                            #   else :
                            #      1. choose next square in the chosen direction
                            #         Iterate.
                            if g_cntr == len(g_s):
                                self._place_word_on_grid(g_s,
                                                         cur_square,
                                                         cur_dir)
                                w_placed = True
                            else:
                                if cur_dir == 'R':
                                    cur_square = (cur_square[0],
                                                  cur_square[1] + 1)
                                elif cur_dir == 'RD':
                                    cur_square = (cur_square[0] + 1,
                                                  cur_square[1] + 1)
                                elif cur_dir == 'D':
                                    cur_square = (cur_square[0] + 1,
                                                  cur_square[1])
                                elif cur_dir == 'L':
                                    cur_square = (cur_square[0],
                                                  cur_square[1] - 1)
                                elif cur_dir == 'LD':
                                    cur_square = (cur_square[0] + 1,
                                                  cur_square[1] - 1)
                                elif cur_dir == 'D':
                                    cur_square = (cur_square[0] + 1,
                                                  cur_square[1])
                                else:
                                    raise Exception('bad direction')
                        else:
                            # If placement fails :
                            #   1. if this is not the first grapheme then
                            #      un-place all the ones that have been placed,
                            #      or discard provisional placement data, if
                            #      that is possible.
                            #   2. iterate to the next initial square
                            break
                        
                    if w_placed:
                        break
                    cur_dir = get_direction(dirs_left)
                    
                if w_placed:
                    self._placed_words.append(g_ent[0])
                    break
                else:       
                    starting_square = get_starting_square(starting_square)
        
        # Future refinements :
        #   1. it is possible to find the starting squares by spiralling out in 
        #      a full circle rather than just a quarter. And depending upon
        #      which side of the centre you are on, you can place the word
        #      backwards starting with the last grapheme. So if you are placing
        #      RTL words you place them from end to start in the upper right
        #      quadrant.
        #   2. we may also want to ensure that to limit expansion that we 
        #      favour place only down and left when in the upper right, and
        #      perhaps in the bottom left we place from the end of the word
        #      left and up. There may be other ways to limit growth.
        #   3. do the graphemes need canonicalization ?
    
    def get_grid(self, output_format='html'):
        '''Get a string representation of the wordsearch in the chosen form.
        
        Parameters
        
        output_format - 'html' an HTML table layout which may be loaded in a
                        browser
        '''
        if output_format == 'html':
            rv = '''
<html>
 <head>
  <meta charset="UTF-8">
    <style>
    div#wordsearch { float: left; width:50%;}
    div#wordlist {float: left; margin-left: 20px;}
    table { width: 100%; border-collapse: collapse;}
    td { font-size: 200%;}
    table, th, td { border: 1px solid black; }
    ul {list-style-type: none;}
  </style>
</head>
<body>
''' + \
        '<div id="header">' + \
        f'''
<h3>Wordsearch</h3>
'''
            # print body including wordsearch grid and list of words
            rv += '<div id="main">'
        
            # wordsearch grid
            rv += '<div id="wordsearch">'
            rv += '<table border="1">' 
            for i in range(self._top, self._bottom+1):
                rv += '<tr>'
                for j in range(self._left, self._right+1):
                    sq = (i, j)
                    if self._grid.get(sq) is not None:
                        rv += f'<td align="center">{self._grid.get(sq)}</td>'
                    else:
                        rv += '<td>.</td>'
                rv += '</tr>'
            rv += '</table></div>'
        
            # print the wordlist
            rv += '''
<div id="wordlist">
<h3>Words to find</h3>
<ul>'''
            for w in sorted(self._words):
                rv += f'<li>{w}</li>'
            rv += '</ul></div>'
        
            # print the footer
            rv += '''
</div>
</div>
</body>
</html>
            '''
            return rv
        elif output_format == 'json':
            def tuple_to_str_keys(m):
                return [{'loc': k, 'grf': v} for k, v in m.items()]
            
            rv = []
            for i in range(self._top, self._bottom+1):
                for j in range(self._left, self._right+1):
                    sq = (i, j)
                    if self._grid.get(sq) is not None:
                        rv.append({'loc': [i, j], 'grf': self._grid.get(sq)})
            return json.dumps(rv, ensure_ascii=False)
        
    def get_word_list(self):
        return self._placed_words
    
    def get_rows(self):
        return abs(self._top - self._bottom) + 1
    
    def get_cols(self):
        return abs(self._right - self._left) + 1
    
    def dump(self, output_format='html', output_file_name=None):
        if output_format == 'html' and output_file_name is not None:
            with open(output_file_name, mode='w', encoding='utf-8') as f:
                f.write(self.get_grid(output_format))
        else:
            raise Exception(f'unsupport output format {output_format}')
        
    def dump_html(self, output_file_name=None):
        '''Print out the wordsearch in the chosen form.
        
        Parameters
        
        output_format - 'html' an HTML table layout which may be loaded in a
                        browser
        output_file_name - a file name to output the dump to
        '''
        print('''
<html>
 <head>
  <meta charset="UTF-8">
    <style>
    div#wordsearch { float: left; width:50%;}
    div#wordlist {float: left; margin-left: 20px;}
    table { width: 100%; border-collapse: collapse;}
    td { font-size: 200%;}
    table, th, td { border: 1px solid black; }
    ul {list-style-type: none;}
  </style>
</head>
<body>
''')
        # print the header with some basic information
        print('<div id="header">')
        print(f'''
<h3>Wordsearch</h3>
<ul>
  <li>Number of words {len(self._words)}.</li>
  <li>top {self._top} left {self._left} bottom {self._bottom} right {self._right}</li>
        ''')
        for s in sorted(self._stat_map.keys()):
            print(f'<li>{s}={self._stat_map.get(s)}</li>')
        print('</ul></div>')
        
        # print body including wordsearch grid and list of words
        print('<div id="main">')
        
        # wordsearch grid
        print('<div id="wordsearch">')
        print('<table border="1">') 
        for i in range(self._top, self._bottom+1):
            print('<tr>')
            for j in range(self._left, self._right+1):
                sq = (i, j)
                if self._grid.get(sq) is not None:
                    print(f'<td align="center">{self._grid.get(sq)}</td>')
                else:
                    print('<td>.</td>')
            print('</tr>')
        print('</table></div>')
        
        # print the wordlist
        print('''
<div id="wordlist">
<h3>Words to find</h3>
<ul>''')
        for w in sorted(self._words):
            print(f'<li>{w}</li>')
        print('</ul></div>')
        
        # print the footer
        print('''
</div>
</div>
</body>
</html>
        ''')

    def fill_empty(self, filler_chars):
        '''Fill the empty slots with random characters from the input list
        of filler characters.
        '''
    
def main(argv=None): # IGNORE:C0111
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    args = parse_command_line(argv[1:])
    command = args.command
    text_name = args.text
    verses = args.verses
    cols = args.cols
    rows = args.rows
    output_format = args.format

    # Check for incompatible options
        
    # Generate a wordsearch
    if command == 'generate':
        
        # parse the verse specification to suit ETCBC
        if text_name == 'ETCBCG':
            refs = expand_refs(convert_refs(parse_refs(verses, form='ETCBCG'),
                                            ReferenceFormID.ETCBCG))
            corpus = Corpus.GREEK
            directions = WordSearch.LTR
        elif text_name == 'ETCBCH':
            refs = expand_refs(convert_refs(parse_refs(verses, form='ETCBCH'),
                                            ReferenceFormID.ETCBCH))
            #refs = expand_refs(parse_refs(verses, form='ETCBCH'))
            corpus = Corpus.HEBREW
            directions = WordSearch.RTL

        # Get the list of words from TF
        sections = []
        [sections.append((r.st_book, r.st_ch, r.st_vs)) for r in refs ]
        word_list = get_words(*sections, work=corpus)

        ws = WordSearch(set(word_list), rows, cols, directions)
        ws.dump(output_format)
        
if __name__ == "__main__":
    if DEBUG:
        # FIXME this is broken - do not use DEBUG without first fixing this
        # the args below are not defined in the parsers
        sys.argv.append("-d")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'puzzleapi.wordsearch.wordsearch_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())