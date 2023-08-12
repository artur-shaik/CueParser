#!/usr/bin/env python
# encoding: utf-8

import os
import re
import sys
import argparse
import math
from datetime import timedelta
from typing import Optional


class CueSheet():

    _fields = [
        "performer",
        "songwriter",
        "title",
        "flags",
        "isrc"
    ]

    outputFormat:str

    def __init__(self):
        self.rem = None
        self.performer = None
        self.songwriter = None
        self.title = None
        self.file = None
        self.aformat = None
        self.tracks = []

        self.iterator = 0

    def setData(self, data):
        self.data = data.split('\n')

    def __next__(self) -> Optional[str]:
        if self.iterator < len(self.data):
            ret = self.data[self.iterator]
            self.iterator += 1
            return ret.strip()
        return None

    def back(self):
        self.iterator -= 1

    def parse(self):
        line = next(self)
        if not line:
            return

        if not self.rem:
            match = re.match('^REM .(.*).$', line)
            rem_tmp = ''
            while match:
                # TODO: maybe os.linesep
                rem_tmp += match.group(0) + '\n'
                line = next(self)
                if line:
                    match = re.match('^REM .(.*).$', line)
            if rem_tmp:
                self.rem = rem_tmp.strip()

        for field in ["performer", "songwriter", "title"]:
            if line and not getattr(self, field):
                match = re.match("^{} .(.*).$".format(field.upper()), line)
                if match:
                    setattr(self, field, match.group(1))
                    line = next(self)

        if line and not self.file:
            match = re.match('^FILE .(.*). (.*)$', line)
            if match:
                self.file = match.group(1)
                self.aformat = match.group(2)
                line = next(self)

        if line:
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
        line = next(self)
        if not line:
            return

        for field in CueSheet._fields:
            match = re.match("^{} .(.*).$".format(field.upper()), line)
            if match:
                setattr(track, field, match.group(1))
                self.track(track)

        match = re.match('^INDEX (.*) (.*)$', line)
        if match:
            track.index = match.group(1)
            track.offset = match.group(2)
            self.track(track)

        self.back()

    def setOutputFormat(self, outputFormat, trackOutputFormat=""):
        self.outputFormat = outputFormat
        self.trackOutputFormat = trackOutputFormat

    def output(self):
        return self.__repr__()

    def getTrackByNumber(self, number):
        return self.tracks[number - 1] if self.tracks[number - 1] else None

    def getTrackByTime(self, time):
        for track in reversed(self.tracks):
            trackOffset = offsetToTimedelta(track.offset)
            if time > trackOffset:
                return track
        return None

    def __repr__(self):
        ret = self.outputFormat
        for field in CueSheet._fields:
            if getattr(self, field):
                ret = ret.replace("%{}%".format(field), getattr(self, field))

        trackOutput = ""
        for track in self.tracks:
            track.setOutputFormat(self.trackOutputFormat)
            trackOutput += "%s\n" % track.output()

        ret = ret.replace("%tracks%", trackOutput)
        return ret


class CueTrack():

    _fields = [
        "performer",
        "songwriter",
        "title",
        "index",
        "offset"
    ]

    outputFormat:str
    number:int

    def __init__(self):
        self.performer = None
        self.songwriter = None
        self.title = None
        self.flags = None
        self.isrc = None
        self.index = None

        self.offset = None
        self.duration = None

    def setOutputFormat(self, outputFormat):
        self.outputFormat = outputFormat

    def output(self):
        return self.__repr__()

    def __repr__(self):
        ret = self.outputFormat

        for field in CueTrack._fields:
            if getattr(self, field):
                ret = ret.replace("%{}%".format(field), getattr(self, field))

        if self.number:
            ret = ret.replace("%number%", "%02d" % self.number)
        if self.duration:
            minutes = math.floor(self.duration.seconds / 60)
            ret = ret.replace("%duration%", "%02d:%02d" %
                              (minutes, self.duration.seconds - 60 * minutes))
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
        if len(offset[2]) < 3:
            offset[2] += "0"
        offset = timedelta(minutes=int(offset[0]), seconds=int(offset[1]),
                           milliseconds=int(offset[2]))
    else:
        print("Wrong offset value")
        exit()
    return offset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--header", help="header output template",
                        default="%performer% - %title%\n%file%\n%tracks%")
    parser.add_argument("-t", "--track", help="track output template",
                        default="%performer% - %title%")
    parser.add_argument("-o", "--offset", help="fetch offset's track")
    parser.add_argument("-n", "--number", help="fetch track by number")
    parser.add_argument("-a", "--all", help="fetch all tracks", default=True)
    parser.add_argument("file", help="path to cue file")
    args = parser.parse_args()

    cuefile = args.file
    if not os.path.isfile(cuefile):
        print("Cannot open file %s" % cuefile)
        exit(2)

    cuesheet = CueSheet()
    cuesheet.setOutputFormat(args.header, args.track)
    with open(cuefile, "rb") as f:
        cuesheet.setData(f.read().decode(sys.stdout.encoding))

    cuesheet.parse()
    try:
        if (args.offset):
            offset = offsetToTimedelta(args.offset)
            print((cuesheet.getTrackByTime(offset)))
        elif (args.number):
            num = int(args.number)
            print((cuesheet.getTrackByNumber(num)))
        elif (args.all):
            print_all_tracks(cuesheet)
        else:
            print((cuesheet.output()))
    except ValueError:
        print("Cannot parse int")
        exit()


def print_all_tracks(cuesheet, i=0):
    for track in cuesheet.tracks:
        i += 1
        print("{}: {}".format(i, track))

if __name__ == '__main__':
    main()
