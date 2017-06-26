# Roadmap
Currently there is just the word search puzzle in this repo.
There are in fact two puzzles in production though, a multi-language alphabet sorting game, and the wordsearch puzzle. The wordsearch is currently non-interactive.

The overall puzzles repository is intended to contain many different word puzzles drawing words from various sources. Sometimes words alone will suffice, and at other times additional information may be required. For example it will be necessary to have definitions to permit generation of clues for crosswords.

The primary purpose of this roadmap is to draw out the requirements on other supporting code and APIs that are not currently obvious.

## Puzzle Catalog
The following puzzles are currently envisaged. All puzzles will be developed supporting multiple languages for content. Whether the UI associated with the puzzles will also be multi-lingual or not will depend upon availability of time and language skills.

Puzzle|Description
------|-----------
Wordsearch|Wordsearch generation and play.
Crossword| Crossword generation and play.
ConvertWord|Given a word change one letter in each step to produce a different and valid word, getting to the final word in the required number of steps.
Scramble|Given a scrambled word reorder the letters to produce the correct original word.
Alphabets|Given a scrambled grid of alphabet letters order them in alphabetical order as appropriate to the chosen alphabet.
Counting|This is a little vague yet. The basic point is that in ancient languages there were ways to represent numbers, often using numerical values attached to certain letters. I would like to develop various mathematical games in these systems, the simplest being to count.
Some sort of Scrabble game| An multi-player online version of Scrabble in dead languages would be really cool.
