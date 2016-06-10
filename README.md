# movie_maker_faces

Runs from command line. Arguments are Files to process (should be matlab files, provided by Guillermo Sapiro's lab) and optional minimum length of movies by fps stripped from lengths of contiguous emotion (default is 30).

Requirements:

- Create 'movies' directory in folder for script to save movies to. Movies will be saved, categorized by emotion, labeled with source file and number (not required to create emotion files before running script).
- Change variable 'emots' to match emotions label in matlab files. Two options in most files, and another, unique option in first files sent.
