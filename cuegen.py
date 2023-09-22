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
        if not self.file and self.performer and self.title:
            self.file = (f'{self.performer.lower().replace(" ", "_")}_-_'
                         f'{self.title.lower().replace(" ", "_")}.'
                         f'{self.file_ext.lower()}')
        return (
        f'PERFORMER "{self.performer}"\n'
        f'TITLE "{self.title}"\n'
        f'FILE "{self.file}" {self.file_ext}')
    

class CueTrack():

    offset: Optional[str] = None

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        if self.offset:
            return (
            '  TRACK 01 AUDIO\n'
            f'    PERFORMER "{self.artist}"\n'
            f'    TITLE "{self.title}"\n'
            f'    INDEX 01 {self.offset}')
        return ""

    def is_parsed(self):
        if self.offset:
            return True
        return False

    def parse(self, line: str):
        match_time = re.match(".*?(\\d{1,2}:\\d{1,2}(:\\d{1,2}|)).*", line)
        if not match_time:
            return
        
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

    tracks = []
    for line in tracklist_data:
        cue_track = CueTrack()
        cue_track.parse(line)
        if cue_track.is_parsed():
            tracks.append(cue_track)
        elif ' - ' in line:
            splitted = line.split(' - ')
            if not cue_title.performer:
                cue_title.performer = splitted[0].strip()
            if not cue_title.title:
                cue_title.title = splitted[1].strip()

    print(cue_title)
    for track in tracks:
        print(track)


if __name__ == "__main__":
    main()
