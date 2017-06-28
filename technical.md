# Technical Notes on puzzles
These notes are really just to quickly document various key technical aspects of the puzzles designs and code.

## Architecture
Currently there are two games, wordsearch and alphabets. Alphabets is very simple and requires no data other than the letters, their canonical ordering and the textual direction.

Wordsearch uses a list of words from some selection from either the Greek NT or Hebrew OT. Currently all processing for production of the wordsearch is done on the server side in Python. This architecture works very well with TextFabric where the data is directly accessible from Python. It has until now been imagined that future enhancements would require the passing more specific query parameters to the server and have it produce the output. Now there are several considerations here. In Hebrew it is possible to produce consonantal or vocalized wordsearches. Now which the user chooses will actually alter the layout of the grid because the removal of duplicates will result in a different final set of words to place. Thus it was imagined that you could not simply have the UI switch modes and have the grid update. Of course one could but then duplicates might appear. There are in fact a few problems like this. In addition it was thought that additional query predicates to select words by parts of speech or some other means would be useful. Again this would change the way the grid appeared and it was thought that the best thing to do was to provide more information to the server and have it provide the appropriate grid.

Now other considerations have come to the fore suggesting that more work ought to be done on the client. Not least of these is the desire to make interactive wordsearch solving possible on the client. Also the desire to simply paste text into the UI and have it produce a wordsearch suggests more having lifting on the client. But further a number of Web APIs make data available in coarser forms than a simple list of words. As a consequence it is necessary either to put in an intermediary layer that will convert from these markup forms to a simple list or to do it on the client directly.

The questions now are different:

  1. Can the client do this much processing to layout a whole wordsearch grid ?
  2. Can TF which has no markup form work in this way also ? Does one have to build an intermediary to convert the rawer simpler format of TF data into markup only to have the client pull it apart ?

## Basic Considerations
The basic requirement of the word games is usually a list of words. It is usual to ensure that there are no duplicates. There are a number of ways this list of words may initially be chosen. In the current wordsearch the word lists are drawn from Greek or Hebrew bible verse searches. Another way would be to cut and paste from a block of text. Additional constraints on choosing the words might run to choosing only the verbs, or the proper names or some such thing. For example, one might do a wordsearch based on the names in the Matthean genealogy.

Crosswords introduce an additional requirement, that of a clue. The simplest possible clue would be a gloss in the user's native language. More complex would be clues as definitions or questions in the native language. The most difficult would be clues in the puzzle language, say for example in Biblical Greek when the crossword is in BG.

ConvertWord is a fun programming problem. Essentially one picks words of the same length and finds all paths through those words which only change a single letter at a time. The question here is what are all the words. For any large number of letters per word you need a fairly large chunk of text to find enough words to choose from. Of course you could also use a lexicon but this has a problem in that the lexical forms are a not all the attested forms and those attested forms increase the number of options and relevance to readers. One could imagine using one entire chapter of Genesis in Hebrew to do this for Hebrew words.

Alphabet sorting games require almost no data, just the alphabet in the appropriate order and thus these games are basically standalone.

Number games need more specification yet before it will be entirely clear what they will require but it is likely that the simpler ones will require data similar to the alphabet games and thus little external support.

## A Heavy Lifting Client Model
A client might get a markup fragment from a source and it might include many different text annotation ranging from morphology, parts of speech, and syntactical information. The client would then be free to create whatever puzzle was wanted using whatever subset of the data the user might choose. The user would not even have to choose the puzzle type before getting the text data from the backend.

#### Graphical Units
In languages such as BH and BG there is considerable use of diacritic marks, BH in particular. Now the thing that is a single graphical unit, what a person would think of as a letter, that is a letter plus its attendent diacritic mark, is not a single Unicode codepoint but a number of them. Most puzzles need at various points to know the number of graphical units for display, for example to correctly allocate spaces in a wordsearch. Now it the BH text though were consonantal rather than including vowels and other markings, then the number of Unicode codepoint per graphical unit is fewer. There are libraries to find this sort of thing out but the point of mentioning it is this. If the puzzle game is constructed entirely on a server then the client needs to express to the server a desire to have either consonantal or vocalized text. If however the client does it then a good deal more work is required on the client but the server does not need to provide so many options; it just provides more data.

Currently graphical units are determined by use of the Python uniseg library. This has threading issues and thus needs to be tweaked to worked on a server. In a client major architecture it would have to be recoded in JS.

## Requirements
In consideration of the above the following basic requirements may be derived.

### Highly Desirable
- A way to obtain a list of words by querying a text for
    - specific passages, identified for example by work, book, chapter, verse

    - by various features of the words including

      - part of speech
      - gender
      - number

      These features might be queried in combination. Other subcategories might also be of interest including

      - names of places
      - names of people

- For Hebrew, a way to obtain words with or without vowel pointing.

- For Greek and Hebrew, a way to obtain the words with and without diacritic marks.

- A way to obtain glosses in a translation language

- A way to obtain definitions from a lexicon

- A way to obtain the lexical form of words

### Required
Failing the ability to obtain any of the above in a compact form, it will be necessary to be able to obtain a document containing this information embedded within markup which the client can then extract the same data from.

### Caveats
It is understood of course that some texts may not offer all the features above. For example the names of places may not be available in a text. In such cases it would useful to know that the feature does not exist.

### Response format
The response can be a simple JSON list where each element is a simple word, or an object containing the word, the lexical entry, the gloss or the definition. Some similar alternative of course could be used. Whatever the form of the response the features requested in the request should be identified by the same name in the response.
