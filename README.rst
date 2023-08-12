CueParser
=========

Simple cue file parser and generator written in python. 
Parser outputs cue file content in plain text. Generator can create cue file from timed tracklist.

Installation
============

**$ pip install CueParser**

Usage
=====

:: 

    usage: cueparser.py [-h] [-H HEADER] [-t TRACK] file

::

    positional arguments:
      file                  path to cue file

    optional arguments:
      -h, --help            show this help message and exit
      -H HEADER, --header HEADER
                            header output template
      -t TRACK, --track TRACK
                            track output template

:: 

    usage: cuegen.py [-h] [-p PERFORMER] [-t TITLE] [-a AUDIO_FILE] [-e AUDIO_FILE_EXT] [-f FILE]

::

    options:
      -h, --help            show this help message and exit
      -p PERFORMER, --performer PERFORMER
                            PERFORMER
      -t TITLE, --title TITLE
                            TITLE
      -a AUDIO_FILE, --audio_file AUDIO_FILE
                            FILE
      -e AUDIO_FILE_EXT, --audio_file_ext AUDIO_FILE_EXT
                            FILE EXTENSION
      -f FILE, --file FILE  path to tracklist file

Example
=======

**$ cueparser.py file.cue**

will output content with such template: 

* for header: %performer% - %title%\\n%file%\\n%tracks% (also can be %format%, %rem%, %songwriter%) 
* for tracks: %performer% - %title% (also can be %offset%, %index%, %songwriter%)

**$ cuegen.py -f file.txt**

will create cue file from tracklist looks like:

    [00:00] Artist 1 - Title 1

    [03:00] Artist 2 - Title 2

    etc...

Library example
===============

.. code:: python 

    cuesheet = CueSheet()
    cuesheet.setOutputFormat(args.header, args.track) 
    with open(cuefile, "r") as f: 
        cuesheet.setData(f.read())

    cuesheet.parse()
    print(cuesheet.output())
