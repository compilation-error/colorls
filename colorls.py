#!/usr/bin/python3
# -*- coding: utf-8 - *-

import os
import glob
from pathlib import Path
import argparse
import pprint
import time
from pwd import getpwuid
from grp import getgrgid


__author__ = "Romeet Chhabra"
__copyright__ = "Copyright 2020, Romeet Chhabra"
__license__ = "MIT"
__version__ = "0.1.0"


METRIC_PREFIXES = ['b', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
METRIC_MULTIPLE = 1024.     # should be 1000. for SI

SUFF = {'dir': '/', 'link': '@', 'exe': '*', 'none': '', 'file': '', 'mount': '', 'this': ''}
ANSI = {'this': '1;39;49', 'dir': '34;49', 'file': '32;49', 'link': '36;49', 'none': '39;49',
                'archive': '31;49', 'mount': '37;49', 'image': '35;49', 'video': '33;49', 'audio': '33;49'}
ICONS = {'this'     : u'\uf07c', 'dir': u'\uf07b', 'file': u'\uf016', 'link': u'\uf838', 'none': u'\uf445',
         'audio'    : u'\uf1c7', 'video': u'\uf1c8', 'image': u'\uf1c5', 'archive': u'\uf1c6',
         '.py'      : u'\uf81f', '.pyc': u'\uf820', '.doc': u'\uf1c2', '.docx': u'\uf1c2', '.docm': u'\uf1c2',
         '.odt'     : u'\uf1c2', '.c': u'\ue61e', '.cpp': u'\ue61d', '.vscode': u'\ue70c', '.vim': u'\ue7c5',
         '.pdf'     : u'\uf1c1', '.zip': u'\uf1c6', '.tar': u'\uf1c6', '.7z': u'\uf1c6', '.key': u'\uf80a',
         '.cur'     : u'\uf245', '.md': u'\uf48a', '.gitignore': u'\ue702', '.git': u'\ue5fb',
         '.AppImage': u'\uf992', '.Appimage': u'\uf992', '.exe': u'\ue62a', '.xml': u'\ufabf', '.html': u'\uf121',
         '.r'       : u'\uf4f7', '.R': u'\uf4f7', 'README': u'\ue28b', 'js': u'\ue74e', '.tar.gz': u'\uf1c6',
         '.gz'      : u'\uf1c6', 'mount': u'\uf0a0', '.php': u'\uf81e', '.json': u'\ue60b', '.yml': u'\ue60b',
         '.sh'      : u'\uf120', '.java': u'\ue738', '.jar': u'\uf53b', '.img': u'\ufaed', '.iso': u'\ufaed'}
ARCHIVE_FORMATS = ['.zip', '.tar', '.tar.gz', '.gz', '.7z']
IMAGE_FORMATS = ['.png', '.tif', '.tiff', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']
VIDEO_FORMATS = ['.wmv', '.mpg', '.mpeg', '.divx', '.xvid', '.mp4', '.mkv']
AUDIO_FORMATS = ['.mp3', '.wma', '.m4a']
DOC_FORMATS = ['.doc', '.docx', '.docm', '.odt']
SPRDSHT_FORMATS = ['.xls', '.xlsx', '.xlsm', '.ods']
PPT_FORMATS = ['.ppt', '.pps', '.pptx', '.odp']


# https://en.wikipedia.org/wiki/ANSI_escape_code
def print_format_table():
    for style in range(9):
        for fg in range(30, 40):
            s1 = ''
            for bg in range(40, 50):
                fmt = ';'.join([str(style), str(fg), str(bg)])
                s1 += f'\x1b[{fmt}m {fmt} \x1b[0m'
            print(s1)
        print('\n')


def get_human_readable_size(size):
    for pre in METRIC_PREFIXES:
        if size < METRIC_MULTIPLE:
            return f"{size:4.0f}{pre}"
        size /= METRIC_MULTIPLE


# TODO: This can be improved - for the category mapping at least. Maybe use a reverse dictionay?
def get_keys(path):
    key1, key2 = 'none', 'none'
    name, n, ext = path.name, path.stem.lower(), path.suffix.lower()
    if ext in ANSI:
        key1 = ext
    elif n in ANSI:
        key1 = n
    elif ext in ARCHIVE_FORMATS:
        key1 = 'archive'
    elif ext in IMAGE_FORMATS:
        key1 = 'image'
    elif ext in VIDEO_FORMATS:
        key1 = 'video'
    elif ext in AUDIO_FORMATS:
        key1 = 'audio'
    elif path.is_symlink():
        key1 = "link"
    elif path.is_dir():
        key1 = "dir"
    elif path.is_file():
        key1 = "file"
    elif path.is_mount():
        key1 = "mount"
    else:
        key1 = "none"
    key2 = key1
    if ext in ICONS:
        key2 = ext
    elif n in ICONS:
        key2 = n
    return key1, key2


def print_tree_listing(path, fmt_key=None, ico_key=None, level=0, pos=0, suffix=""):
    tree_str = "   |   " * level + "   " + u'\u25ba' + "---"
    print(tree_str, end="")
    print_short_listing(path, expand=True, end='\n')


def print_long_listing(path, is_numeric=False):
    try:
        st = path.stat()
        size = st.st_size
        sz = get_human_readable_size(size)
        mtime = time.ctime(st.st_mtime)
        mode = os.path.stat.filemode(st.st_mode)
        uid = getpwuid(st.st_uid).pw_name if not is_numeric else str(st.st_uid)
        gid = getgrgid(st.st_gid).gr_name if not is_numeric else str(st.st_gid)
        hln = st.st_nlink
        print(f"{mode} {hln:3} {uid:4} {gid:4} {sz} {mtime} ", end="")
        print_short_listing(path, expand=True, end='\n')
    except FileNotFoundError as e:
        ...    # TODO: Handle this better. What feedback should be given to the user?


def print_short_listing(path, fmt_key=None, ico_key=None, expand=False, tag=False, sep_len=None, end='\t'):
    fmt, ico = get_keys(path)
    name = path.name
    if expand and path.is_symlink():
        name += " -> " + str(path.resolve())
    name += SUFF[fmt] if tag else ""
    # Pretty certain using default sep_len is going to create issues
    sep_len = sep_len if sep_len else len(name) + 1
    print(f"\x1b[{ANSI[fmt]}m {ICONS[ico]} {name:<{sep_len}}\x1b[0m", end=end)


def process_dir(directory, args, level=0, size=None):
    report = dict()
    contents, files, subs = list(), list(), list()

    try:
        p = Path(directory)
        if p.exists() and p.is_dir():
            if level == 0:
                print()
                print_short_listing(p.absolute(), fmt_key='this', ico_key='this', end=':\n')
            contents = list(p.iterdir())
            if args.ignore:
                remove_list = list(p.glob(args.ignore))
                contents = [c for c in contents if c not in remove_list]
            files = [x for x in contents if x.is_file()]
            subs = [x for x in contents if x.is_dir()]
        elif p.exists() and p.is_file():
            contents = [p]
        else:
            contents = list(Path('.').glob(directory))
    except Exception as e:
        ...  #TODO: This should be a little more graceful!

    contents = sorted(contents)

    if args.directory:
        entries = subs
    elif args.file:
        entries = files
    else:
        entries = contents

    # TODO: A more elegent solution to aligning short print listing. This is an aweful hack!
    longest_entry = max([len(str(x.name)) for x in entries]) if len(entries) > 0 else None
    if longest_entry and size:
        max_items = size[0] // (longest_entry + 10)     # 10 is just a buffer amount. can be updated if not pretty
    else:
        max_items = 9999999
    run = 0
    end = "\n" if vars(args)['1'] else "\t"
    for path in entries:
        if not args.all and path.name.startswith('.'):
            continue
        if args.ignore_backups and path.name.endswith('~'):
            continue
        if args.long or args.numeric_uid_gid:
            print_long_listing(path, is_numeric=args.numeric_uid_gid)
        elif args.tree and args.tree > 0:
            print_tree_listing(path, level=level)
            if path.is_dir() and level < args.tree - 1:
                report['/' + path.name] = process_dir(path, args, level=level+1, size=size)[path]
        else:
            print_short_listing(path, sep_len=longest_entry, tag=args.classify, end=end)
            run += 1
            if run >= max_items:
                print()
                run = 0

    if args.recursive and not args.tree:
        for sub in subs:
            report['/' + sub.name] = process_dir(sub, args, size=size)[sub]

    rep = dict()
    rep['files'] = len(files)
    rep['dirs'] = len(subs)
    report[directory] = rep
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-1", action="store_true", default=False, help="list items on individual lines")
    parser.add_argument("-a", "--all", action="store_true", default=False, help="do not ignore entires starting with .")
    parser.add_argument("-B", "--ignore-backups", action="store_true", default=False,
                        help="do not list implied entires ending with ~")
    parser.add_argument("-d", "--directory", action="store_true", default=False,
                        help="list directories themselves, not their contents")
    parser.add_argument("-f", "--file", action="store_true", default=False, help="list files only, not directories")
    parser.add_argument("-F", "--classify", action="store_true",
                         default=False, help="append indicator (one of */=>@|) to entries")
    parser.add_argument("-I", "--ignore", metavar="PATTERN", help="do not list implied entries matching shell PATTERN")
    parser.add_argument("-l", "--long", action="store_true", default=False, help="use a long listing format")
    parser.add_argument("-n", "--numeric-uid-gid", action="store_true",
                        default=False, help="like -l, but list numeric user and group IDs")
    parser.add_argument("-R", "--recursive", action="store_true", default=False, help='list subdirectories recursively')
    parser.add_argument("--report", action="store_true", default=False,
                        help="brief report about number of files and directories")
    parser.add_argument("-t", "--tree", metavar="DEPTH", type=int, nargs='?', const=3, help="max tree depth")
    parser.add_argument("--version", action="store_true", default=False, help="display current version number")
    parser.add_argument("FILE", default=".", nargs=argparse.REMAINDER,
                        help="List information about the FILEs (the current directory by default).")
    args = parser.parse_args()
    if args.version:
        print("colorls.py version " + __version__)

    try:
        term_size = os.get_terminal_size()
    except Exception as e:
        ...     # this can be quiet, since this is optional, sorta

    if not args.FILE:
        args.FILE = ["."]

    report = list()
    for FILE in args.FILE:
        report.append(process_dir(FILE, args, size=term_size))
        print()

    # TODO: Fix report - only shows current directory and next correctly. Likely overwritten dictionary values
    if args.report and report:
        print("\n --- REPORT ---")
        for n in report:
            for k,v in reversed(n.items()):
                print(f"{k} -> {v}")

# vim: ts=4 sts=4 sw=4 et syntax=python:
