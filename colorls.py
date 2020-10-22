import os
import glob
import argparse
import pprint
import time
from pwd import getpwuid
from grp import getgrgid

METRIC_PREFIXES = ['b', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
METRIC_MULTIPLE = 1024.
LEND = '\t'
ANSI_FORMATS = {'this': '1;39;49', 'dir': '34;49', 'file': '32;49', 'link': '4;36;49', 'none': '39;49'}
# https://fontawesome.com/cheatsheet/free
ICONS = {'this'     : u'\uf07c', 'dir': u'\uf07b', 'file': u'\uf15b', 'link': u'\uf35d', 'none': u'\uf0c8',
         '.py'      : u'\uf3e2', '.pyc': u'\uf3e2', '.doc': u'\uf1c2', '.docx': u'\uf1c2', '.docm': u'\uf1c2',
         '.odt'     : u'\uf1c2',
         '.pdf'     : u'\uf1c1', '.zip': u'\uf1c6', '.tar': u'\uf1c6', '.7z': u'\uf1c6', '.key': u'\uf084',
         '.cur'     : u'\uf245', '.sh': u'\uf1c9', '.md': u'\uf60f', '.gitignore': u'\uf841', '.git': u'\uf1d3',
         '.AppImage': u'\uf5ba', '.Appimage': u'\uf5ba', '.exe': u'\uf3ca', '.xml': u'\uf121', '.html': u'\uf121',
         '.r'       : u'\uf4f7', '.R': u'\uf4f7', 'README': u'\uf4d5', 'js': u'\uf3b8'}


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
	if os.path.isdir(path):
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


def print_tree_listing(path):
	...


def print_long_listing(path, fmt_key=None, ico_key=None, sep=',', end='\n'):
	try:
		st = os.stat(path)
		size = st.st_size
		sz = get_human_readable_size(size)
		mtime = time.ctime(st.st_mtime)
		mode = os.path.stat.filemode(st.st_mode)
		uid = getpwuid(st.st_uid).pw_name
		gid = getgrgid(st.st_gid).gr_name
		hln = st.st_nlink

		name = os.path.basename(path)
		fmt = ANSI_FORMATS[fmt_key] if fmt_key else get_fmt(path)
		ico = ICONS[ico_key] if ico_key else get_ico(path)
		print(f"\x1b[{fmt}m {mode} {hln:3} {uid:4} {gid:4} {sz} {mtime} {ico} {name} \x1b[0m", sep=sep, end=end)
	except FileNotFoundError as e:
		print(e)


def print_short_listing(path, fmt_key=None, ico_key=None, sep=',', end=None):
	name = os.path.basename(path)
	fmt = ANSI_FORMATS[fmt_key] if fmt_key else get_fmt(path)
	ico = ICONS[ico_key] if ico_key else get_ico(path)
	print(f"\x1b[{fmt}m {ico} {name} \x1b[0m", sep=sep, end=end if end else LEND)


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
	parser.add_argument("-n", "--no-icons", action="store_true", default=False, help="do not use icons")
	parser.add_argument("-R", "--recursive", action="store_true", default=False, help='list subdirectories recursively')
	parser.add_argument("--report", action="store_true", default=False,
	                    help="brief report about number of files and directories")
	parser.add_argument("-t", "--tree-depth", type=int, metavar="DEPTH", default=3, help="max tree depth")
	parser.add_argument("FILE", default=".", nargs=argparse.REMAINDER, help="directory you want to list")
	args = parser.parse_args()

	LEND = "\n" if vars(args)['1'] else "\t"
	if not args.FILE:
		args.FILE = ["."]

	report = dict()
	for FILE in args.FILE:
		rep = dict()
		for dirs, subs, files in os.walk(FILE):
			print_short_listing(os.path.abspath(dirs), fmt_key='this', ico_key='this', end=':\n')

			if not args.directory:
				for name in files:
					if not args.all and name.startswith('.'):
						continue
					if args.ignore_backups and name.endswith('~'):
						continue
					path = os.path.abspath(os.path.join(dirs, name))
					if not args.long:
						print_short_listing(path)
					else:
						print_long_listing(path)

			if not args.file:
				for name in subs:
					if not args.all and name.startswith('.'):
						continue
					path = os.path.abspath(os.path.join(dirs, name))
					if not args.long:
						print_short_listing(path)
					else:
						print_long_listing(path)

			print('\n')
			if not args.recursive:
				break

		if args.report:
			rep['files'] = len(files)
			rep['subs'] = len(subs)
			report[FILE] = rep

	if args.report:
		pprint.pprint(report)
