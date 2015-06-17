#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import re
import argparse
import math
from datetime import timedelta

class CueSheet():

    def __init__(self):
        self.rem = None
        self.performer = None
        self.songwriter = None
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

        if not self.rem:
            match = re.match('^REM .(.*).$', line)
            rem_tmp = ''
            while match:
                rem_tmp += match.group(0) +'\n'
                line = self.next()
                match = re.match('^REM .(.*).$', line)
            if rem_tmp:
                self.rem = rem_tmp.strip()
        
        if not self.performer:
            match = re.match('^PERFORMER .(.*).$', line)
            if match:
                self.performer = match.group(1)
                line = self.next()

        if not self.songwriter:
            match = re.match('^SONGWRITER .(.*).$', line)
            if match:
                self.songwriter = match.group(1)
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
            cuetrack.setOutputFormat(self.trackOutputFormat)
            cuetrack.number = len(self.tracks) + 1
            self.track(cuetrack)
            if len(self.tracks) > 0:
                previous = self.tracks[len(self.tracks) - 1]
                offset = offsetToTimedelta(cuetrack.offset)
                previosOffset = offsetToTimedelta(previous.offset)
                previous.duration = offset - previosOffset

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

        match = re.match('^SONGWRITER .(.*).$', line)
        if match:
            track.songwriter = match.group(1)
            self.track(track)

        match = re.match('^TITLE .(.*).$', line)
        if match:
            track.title = match.group(1)
            self.track(track)

        match = re.match('^FLAGS .(.*).$', line)
        if match:
            track.flags = match.group(1)
            self.track(track)

        match = re.match('^ISRC .(.*).$', line)
        if match:
            track.ISRC = match.group(1)
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
        return self.__repr__()

    def getTrackByNumber(self, number):
        if self.tracks[number - 1]: return self.tracks[number - 1]
        return None

    def getTrackByTime(self, time):
        for track in reversed(self.tracks):
            trackOffset = offsetToTimedelta(track.offset)
            if time > trackOffset: return track

        return None

    def __repr__(self):
        ret = self.outputFormat
        if self.rem:
            ret = ret.replace("%rem%", self.rem)
        if self.performer:
            ret = ret.replace("%performer%", self.performer)
        if self.songwriter:
            ret = ret.replace("%songwriter%", self.songwriter)
        if self.title:
            ret = ret.replace("%title%", self.title)
        if self.file:
            ret = ret.replace("%file%", self.file)
        if self.aformat:
            ret = ret.replace("%format%", self.aformat)

        trackOutput = ""
        for track in self.tracks:
            track.setOutputFormat(self.trackOutputFormat)
            trackOutput += "%s\n" % track.output()

        ret = ret.replace("%tracks%", trackOutput)
        return ret

class CueTrack():
    def __init__(self):
        self.performer = None
        self.songwriter = None
        self.title = None
        self.flags = None
        self.isrc = None
        self.index = None

        self.offset = None
        self.outputFormat = None
        self.duration = None
        self.number = None

    def setOutputFormat(self, outputFormat):
        self.outputFormat = outputFormat

    def output(self):
        return self.__repr__();

    def __repr__(self):
        ret = self.outputFormat
        if self.performer:
            ret = ret.replace("%performer%", self.performer)
        if self.songwriter:
            ret = ret.replace("%songwriter%", self.songwriter)
        if self.title:
            ret = ret.replace("%title%", self.title)
        if self.index:
            ret = ret.replace("%index%", self.index)
        if self.offset:
            ret = ret.replace("%offset%", self.offset)
        if self.number:
            ret = ret.replace("%number%", "%02d" % self.number)
        if self.duration:
            minutes = math.floor(self.duration.seconds / 60)
            ret = ret.replace("%duration%", "%02d:%02d" % (minutes, self.duration.seconds - 60 * minutes));
        else:
            ret = ret.replace("%duration%", "")

        return ret

def offsetToTimedelta(offset):
    offset = offset.split(':')
    if len(offset) == 1:
        offset = timedelta(minutes=int(offset[0]))
    elif len(offset) == 2:
        offset = timedelta(minutes=int(offset[0]), seconds=int(offset[1]))
    elif len(offset) == 3:
        if len(offset[2]) < 3: offset[2] += "0"
        offset = timedelta(minutes=int(offset[0]), seconds=int(offset[1]), milliseconds=int(offset[2]))
    else:
        print("Wrong offset value")
        exit()
    return offset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-H", "--header", help="header output template", default="%performer% - %title%\n%file%\n%tracks%" )
    parser.add_argument( "-t", "--track", help="track output template", default="%performer% - %title%" )
    parser.add_argument( "-o", "--offset", help="fetch offset's track" )
    parser.add_argument( "-n", "--number", help="fetch track by number" )
    parser.add_argument( "file", help="path to cue file" )
    args = parser.parse_args();

    cuefile = args.file
    if not os.path.isfile(cuefile):
        print("Cannot open file %s" % cuefile)
        exit(2)

    cuesheet = CueSheet()
    cuesheet.setOutputFormat(args.header, args.track)
    with open(cuefile, "rb") as f:
        cuesheet.setData(f.read().decode('latin-1'))

    cuesheet.parse()
    try:
        if (args.offset):
            offset = offsetToTimedelta(args.offset)
            print(cuesheet.getTrackByTime(offset))
        elif (args.number):
            num = int(args.number)
            print(cuesheet.getTrackByNumber(num))
        else:
            print(cuesheet.output())
    except ValueError:
        print("Cannot parse int")
        exit()

if __name__ == '__main__':
    main()
