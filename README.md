CueParser
=========

Simple cue file parser written in python. Outputs cue file content in plain text. Could be used like library.

Usage
=====

```
usage: cueparser.py [-h] [-H HEADER] [-t TRACK] file

positional arguments:
  file                  path to cue file

optional arguments:
  -h, --help            show this help message and exit
  -H HEADER, --header HEADER
                        header output template
  -t TRACK, --track TRACK
                        track output template
```

Example
=======

`cueparser.py file.cue`

will output content with such template:
* for header: %performer% - %title%\n%file%\n%tracks% (also can be %format%)
* for tracks: %performer% - %title% (also can be %offset%, %index%)

Library example
===============

```
    cuesheet = CueSheet()
    cuesheet.setOutputFormat(args.header, args.track)
    with open(cuefile, "r") as f:
        cuesheet.setData(f.read())

    cuesheet.parse()
    print(cuesheet.output())
```
