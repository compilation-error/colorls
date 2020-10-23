import os
import glob
from pathlib import Path
import argparse
import pprint
import time
from pwd import getpwuid
from grp import getgrgid

METRIC_PREFIXES = ['b', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
METRIC_MULTIPLE = 1024.
LEND = '\t'
SIZE = None
SCREEN_BUFFER = 10
ANSI_FORMATS = {'this': '1;39;49', 'dir': '34;49', 'file': '32;49', 'link': '4;36;49', 'none': '39;49',
				'archive': '31;49', 'mount': '37;49', 'image': '35;49', 'video': '33;49', 'audio': '33;49'}
# https://fontawesome.com/cheatsheet/free
ICONS = {'this'     : u'\uf07c', 'dir': u'\uf07b', 'file': u'\uf15b', 'link': u'\uf35d', 'none': u'\uf0c8',
         '.py'      : u'\uf81f', '.pyc': u'\uf820', '.doc': u'\uf1c2', '.docx': u'\uf1c2', '.docm': u'\uf1c2',
         '.odt'     : u'\uf1c2', '.c': u'\ue61e', '.cpp': u'\ue61d', '.vscode': u'\ue70c', '.vim': u'\ue7c5',
         '.pdf'     : u'\uf1c1', '.zip': u'\uf1c6', '.tar': u'\uf1c6', '.7z': u'\uf1c6', '.key': u'\uf084',
         '.cur'     : u'\uf245', '.sh': u'\uf1c9', '.md': u'\uf48a', '.gitignore': u'\uf841', '.git': u'\uf1d3',
         '.AppImage': u'\uf5ba', '.Appimage': u'\uf5ba', '.exe': u'\uf3ca', '.xml': u'\uf121', '.html': u'\uf121',
         '.r'       : u'\uf4f7', '.R': u'\uf4f7', 'README': u'\uf4d5', 'js': u'\uf3b8', '.tar.gz': u'\uf1c6',
		 '.gz'      : u'\uf1c6', 'mount': u'\uf0a0'}
ARCHIVE_FORMATS = ['.zip', '.tar', '.tar.gz', '.gz', '.7z']
IMAGE_FORMATS = ['.png', '.tif', '.tiff', '.jpg', '.jpeg', '.gif']
VIDEO_FORMATS = ['.wmv', '.mpg', '.mpeg', '.divx', '.xvid', '.mp4', '.mkv']
AUDIO_FORMATS = ['.mp3', '.wma', '.m4a']

# apple:     f179
# android:     f17b
# angular:     f420
# aws:     f375
# docker:     f395
# git:     f841
# github:     f09b
# gitlab:     f296
# js:     f3b8
# tux:     f17c
# ms:     f3ca
# node:     f419
# node-js:     f3d3
# npm:     f3d4
# R:     f4f7
# Readme:     f4d5
# rust:     e07a
# safari:     f267
# sass:     f41e
# steam:     f1b6
# usb:     f287
# unity:     e049
# vuejs;     f41f
# windows:     f17a
# ruby/gem:     f3a5
# mounted hdd;     f0a0
#

# https://en.wikipedia.org/wiki/ANSI_escape_code
def print_format_table():
	for style in range(9):
		for fg in range(30, 40):
			s1 = ''
			for bg in range(40, 50):
				format = ';'.join([str(style), str(fg), str(bg)])
				s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
			print(s1)
		print('\n')


def get_human_readable_size(size):
	for pre in METRIC_PREFIXES:
		if size < METRIC_MULTIPLE:
			return f"{size:4.0f}{pre}"
		size /= METRIC_MULTIPLE


def get_fmt(path):
	name = os.path.basename(path)
	n, ext = os.path.splitext(name)
	n, ext = n.lower(), ext.lower()
	if ext in ARCHIVE_FORMATS:
		fmt_key = 'archive'
	elif ext in IMAGE_FORMATS:
		fmt_key = 'image'
	elif ext in VIDEO_FORMATS:
		fmt_key = 'video'
	elif ext in AUDIO_FORMATS:
		fmt_key = 'audio'
	elif ext in ANSI_FORMATS:
		fmt_key = ext
	elif n in ANSI_FORMATS:
		fmt_key = n
	elif os.path.isdir(path):
		fmt_key = "dir"
	elif os.path.isfile(path):
		fmt_key = "file"
	elif os.path.islink(path):
		fmt_key = "link"
	elif os.path.ismount(path):
		fmt_key = "mount"
	else:
		fmt_key = "none"
	return ANSI_FORMATS[fmt_key]


def get_ico(path):
	name = os.path.basename(path)
	n, ext = os.path.splitext(name)
	n, ext = n.lower(), ext.lower()
	if ext in ICONS:
		ico_key = ext
	elif n in ICONS:
		ico_key = n
	elif os.path.isdir(path):
		ico_key = "dir"
	elif os.path.isfile(path):
		ico_key = "file"
	elif os.path.islink(path):
		ico_key = "link"
	elif os.path.ismount(path):
		ico_key = "mount"
	else:
		ico_key = "none"
	return ICONS[ico_key]


def print_tree_listing(path, fmt_key=None, ico_key=None, level=0, pos=0):
	name = os.path.basename(path)
	fmt = ANSI_FORMATS[fmt_key] if fmt_key else get_fmt(path)
	ico = ICONS[ico_key] if ico_key else get_ico(path)
	tree_str = "   |   " * level + "   " + u'\u25ba' + "---" #2ba1  25ba
	print(f"\x1b[{fmt}m {tree_str} {ico} {name} \x1b[0m")


def print_long_listing(path, fmt_key=None, ico_key=None, is_numeric=False, sep=',', end='\n'):
	try:
		st = os.stat(path)
		size = st.st_size
		sz = get_human_readable_size(size)
		mtime = time.ctime(st.st_mtime)
		mode = os.path.stat.filemode(st.st_mode)
		uid = getpwuid(st.st_uid).pw_name if not is_numeric else str(st.st_uid)
		gid = getgrgid(st.st_gid).gr_name if not is_numeric else str(st.st_gid)
		hln = st.st_nlink

		name = os.path.basename(path)
		fmt = ANSI_FORMATS[fmt_key] if fmt_key else get_fmt(path)
		ico = ICONS[ico_key] if ico_key else get_ico(path)
		print(f"\x1b[{fmt}m {mode} {hln:3} {uid:4} {gid:4} {sz} {mtime} {ico} {name} \x1b[0m", sep=sep, end=end)
	except FileNotFoundError as e:
		print(e)	# TODO: This should be a litle more graceful than throwing up the error.


def print_short_listing(path, fmt_key=None, ico_key=None, sep=None, end=None):
	name = os.path.basename(path)
	fmt = ANSI_FORMATS[fmt_key] if fmt_key else get_fmt(path)
	ico = ICONS[ico_key] if ico_key else get_ico(path)
	_sep = sep if sep else len(name)
	print(f"\x1b[{fmt}m {ico} {name:<{_sep}}\x1b[0m", end=end if end else LEND)


def process_dir(directory, args, level=0, size=None):
	rep = dict()
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
		print(f"{e=}")	#TODO: This should be a little more graceful as well!

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
		max_items = size[0] // (longest_entry + SCREEN_BUFFER)
	else:
		max_items = 9999999
	run = 0
	for entry in entries:
		if not args.all and entry.name.startswith('.'):
			continue
		if args.ignore_backups and entry.name.endswith('~'):
			continue
		path = entry.resolve()
		if args.long or args.numeric_uid_gid:
			print_long_listing(path, is_numeric=args.numeric_uid_gid)
		elif args.tree and args.tree > 0:
			print_tree_listing(path, level=level)
			if path.is_dir() and level < args.tree - 1:
				process_dir(path, args, level=level+1, size=size)
		else:
			print_short_listing(path, sep=longest_entry)
			run += 1
			if run >= max_items:
				print()
				run = 0

	if args.recursive:
		for sub in subs:
			process_dir(sub, args, size=size)

	if args.report:
		rep['files'] = len(files)
		rep['subs'] = len(subs)
		report[FILE] = rep


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-1", action="store_true", default=False, help="list items on individual lines")
	parser.add_argument("-a", "--all", action="store_true", default=False, help="do not ignore entires starting with .")
	parser.add_argument("-B", "--ignore-backups", action="store_true", default=False,
	                    help="do not list implied entires ending with ~")
	parser.add_argument("-d", "--directory", action="store_true", default=False,
	                    help="list directories themselves, not their contents")
	parser.add_argument("-f", "--file", action="store_true", default=False, help="list files only, not directories")
	parser.add_argument("-I", "--ignore", metavar="PATTERN", help="do not list implied entries matching shell PATTERN")
	parser.add_argument("-l", "--long", action="store_true", default=False, help="use a long listing format")
	parser.add_argument("-n", "--numeric-uid-gid", action="store_true",
	                    default=False, help="like -l, but list numeric user and group IDs")
	parser.add_argument("-R", "--recursive", action="store_true", default=False, help='list subdirectories recursively')
	parser.add_argument("--report", action="store_true", default=False,
	                    help="brief report about number of files and directories")
	parser.add_argument("-t", "--tree", metavar="DEPTH", type=int, nargs='?', const=3, help="max tree depth")
	parser.add_argument("FILE", default=".", nargs=argparse.REMAINDER, help="directory you want to list")
	args = parser.parse_args()
	print(args)

	LEND = "\n" if vars(args)['1'] else "\t"
	try:
		SIZE = os.get_terminal_size()
	except Exception as e:
		print(f"Error getting terminal size, {e}")
	print(SIZE)
	p = Path('.')
	if not args.FILE:
		args.FILE = ["."]

	report = dict()
	for FILE in args.FILE:
		process_dir(FILE, args, size=SIZE)
		print()

	if args.report:
		print()
		pprint.pprint(report)
