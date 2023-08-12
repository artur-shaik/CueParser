#!/usr/bin/env python
# encoding: utf-8

import argparse
import os
import re
import sys
from typing import Optional
from dateutil.parser import parse


class CueTitle():

    performer: Optional[str] = None
    title: Optional[str] = None
    file: Optional[str] = None
    file_ext: str = 'MP3'

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return (
        f'PERFORMER "{self.performer}"\n'
        f'TITLE "{self.title}"\n'
        f'FILE "{self.file}" {self.file_ext}')
    

class CueTrack():

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return (
        '  TRACK 01 AUDIO\n'
        f'    PERFORMER "{self.artist}"\n'
        f'    TITLE "{self.title}"\n'
        f'    INDEX 01 {self.offset}')

    def parse(self, line: str):
        match_time = re.match(".*?(\\d{1,2}:\\d{1,2}(:\\d{1,2}|)).*", line)
        if not match_time:
            exit("couldn't find time markers")
        
        time = None
        if match_time.group(1).count(":") == 1:
            time = parse(f"00:{match_time.group(1)}")
        else:
            time = parse(match_time.group(1))
        line = re.sub(f"(\\[|\\(|){match_time.group(1)}(\\]|\\)|)", "", line)
        artist = None
        title = None
        for split in line.split("-"):
            if not artist:
                artist = split.strip()
            elif not title:
                title = split.strip()

        self.offset = (f"{str(time.hour * 60 + time.minute).zfill(2)}:"
                       f"{str(time.second).zfill(2)}:00")
        self.artist = artist
        self.title = title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--performer", help="PERFORMER")
    parser.add_argument("-t", "--title", help="TITLE")
    parser.add_argument("-a", "--audio_file", help="FILE")
    parser.add_argument("-e", "--audio_file_ext", help="FILE EXTENSION", default='MP3')
    parser.add_argument("-f", "--file", help="path to tracklist file")
    args = parser.parse_args()

    cue_title = CueTitle()

    if args.performer:
        cue_title.performer = args.performer
    if args.title:
        cue_title.title = args.title
    if args.audio_file:
        cue_title.file = args.audio_file
    if args.audio_file_ext:
        cue_title.file_ext = args.audio_file_ext

    tracklist_data = None
    if args.file:
        tracklist = args.file
        if not os.path.isfile(tracklist):
            print("Cannot open file %s" % tracklist)
            exit(2)
        
        if not cue_title.file:
            file_name = os.path.splitext(os.path.basename(args.file))[0]
            cue_title.file = f'{file_name}.{args.audio_file_ext.lower()}'
        with open(tracklist, "r") as file:
            tracklist_data = file.readlines()
    else:
        tracklist_data = [line for line in sys.stdin]

    print(cue_title)
    for line in tracklist_data:
        cue_track = CueTrack()
        cue_track.parse(line)
        print(cue_track)


if __name__ == "__main__":
    main()
