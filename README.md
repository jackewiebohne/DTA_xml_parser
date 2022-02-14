# DTA_xml_parser
## this project is obsolete. It is a primitive deterministic parser

A parser for the xml files of the Deutsche Textarchiv which outputs a csv (if desired)

It parses: author (firstname, surname), publishing location, publication date, title, text, geodata (i.e. (Spanish, German, Austrian, UK, Swiss, Polish, French, Italian) cities or countries mentioned (by their German name) in the texts), people mentioned in the texts (e.g. Goethe may mention Schlegel in one of his texts). (Polish cities are parsed for their German names, due to the fact that Prussia once occupied large parts of today's Poland)

The parser also includes:
  1) a punctuation remover that also (optionally) normalises some of the older texts' spelling quirks.
  2) a function that converts (most) city names in Germany from Latin to German
  3) a function called wordlabeler that (despite its more general name) checks the texts & titles for geodata (e.g. German cities) and then outputs a list that states that (e.g.) it's found a German city, the name of the city, and the number of occurrences. Sample output of the wordlabeler looks like this: ['ITALIAN_CITY:', 'Rom', 9] , or also: ['ITALIAN_CITY:', 'Rom', 11, 'GERMAN_CITY:', 'Regensburg', 'ITALIAN_CITY:', 'Venedig']. This can (should!) be appended to other output (like date, authorname..) to a csv.

Parsing for geodata will take a long time (several hours on my laptop). The parser can be stopped and then run again to pick up at the last parse (this is the default setting, unless you change the filename/filelocation that is put into the function as function parameter.
Feel free to test if it's faster with Pypy (there should be some decent speed gains).

I've also built a csv cleaner for the parser to get rid of some clutter and special characters as well as to filter country-specific geodata, unique geodata, etc.
