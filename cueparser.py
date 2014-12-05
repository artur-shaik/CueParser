#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import re
import argparse

class CueSheet():

    def __init__(self):
        self.performer = None
        self.title = None
        self.file = None
        self.aformat = None
        self.tracks = []
        self.outputFormat = None

        self.iterator = 0

    def setData(self, data):
        self.data = data.split('\n')

    def next(self):
        if self.iterator < len(self.data):
            ret = self.data[self.iterator]
            self.iterator += 1
            return ret.strip()
        return None

    def back(self):
        self.iterator -= 1

    def parse(self):
        line = self.next()
        if not line:
            return

        if not self.performer:
            match = re.match('^PERFORMER .(.*).$', line)
            if match:
                self.performer = match.group(1)
                line = self.next()

        if not self.title:
            match = re.match('^TITLE .(.*).$', line)
            if match:
                self.title = match.group(1)
                line = self.next()

        if not self.file:
            match = re.match('^FILE .(.*). (.*)$', line)
            if match:
                self.file = match.group(1)
                self.aformat = match.group(2)
                line = self.next()

        match = re.match('^TRACK.*$', line)
        if match:
            cuetrack = CueTrack()
            self.track(cuetrack)
            self.tracks.append(cuetrack)

        self.parse()

    def track(self, track):
        line = self.next()
        if not line:
            return

        match = re.match('^PERFORMER .(.*).$', line)
        if match:
            track.performer = match.group(1)
            self.track(track)

        match = re.match('^TITLE .(.*).$', line)
        if match:
            track.title = match.group(1)
            self.track(track)

        match = re.match('^INDEX (.*) (.*)$', line)
        if match:
            track.index = match.group(1)
            track.offset = match.group(2)
            self.track(track)

        self.back()

    def setOutputFormat(self, outputFormat, trackOutputFormat = ""):
        self.outputFormat = outputFormat
        self.trackOutputFormat = trackOutputFormat

    def output(self):
        ret = self.outputFormat
        if self.performer:
            ret = ret.replace("%performer%", self.performer)
        if self.title:
            ret = ret.replace("%title%", self.title)
        if self.file:
            ret = ret.replace("%file%", self.file)
        if self.aformat:
            ret = ret.replace("%aformat%", self.aformat)

        trackOutput = ""
        for track in self.tracks:
            track.setOutputFormat(self.trackOutputFormat)
            trackOutput += "%s\n" % track.output()

        ret = ret.replace("%tracks%", trackOutput)
        return ret

    def __repr__(self):
        header = "Title: %s - %s\nFile name: %s\nFile format: %s\n" % (self.performer, self.title, self.file, self.aformat)
        body = ""
        for line in self.tracks:
            body += "%sn" % line

        return "%s%s" % (header, body)

class CueTrack():
    def __init__(self):
        self.performer = None
        self.title = None
        self.index = None
        self.offset = None
        self.outputFormat = None

    def setOutputFormat(self, outputFormat):
        self.outputFormat = outputFormat

    def output(self):
        ret = self.outputFormat
        if self.performer:
            ret = ret.replace("%performer%", self.performer)
        if self.title:
            ret = ret.replace("%title%", self.title)
        if self.index:
            ret = ret.replace("%index%", self.index)
        if self.offset:
            ret = ret.replace("%offset%", self.offset)

        return ret

    def __repr__(self):
        return "%s - %s\t %s\n" % (self.performer, self.title, self.offset)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-H", "--header", help="header output template", default="%performer% - %title%\n%file%\n%tracks%" )
    parser.add_argument( "-t", "--track", help="track output template", default="%performer% - %title%" )
    parser.add_argument( "file", help="path to cue file" )
    args = parser.parse_args();

    cuefile = args.file
    if not os.path.isfile(cuefile):
        print("Cannot open file %s" % cuefile)
        exit(2)

    cuesheet = CueSheet()
    cuesheet.setOutputFormat(args.header, args.track)
    with open(cuefile, "r") as f:
        cuesheet.setData(f.read())

    cuesheet.parse()
    print(cuesheet.output())

if __name__ == '__main__':
    main()
