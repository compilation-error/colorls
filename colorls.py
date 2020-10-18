import os
import glob
import argparse

# https://en.wikipedia.org/wiki/ANSI_escape_code
def print_format_table():
    for style in range(9):
        for fg in range(30,40):
            s1 = ''
            for bg in range(40,50):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')

type_fmt = {'this':'1;39;49', 'dir':'34;49', 'file':'32;49', 'link':'4;36;49'}
# https://fontawesome.com/cheatsheet/free/brands
type_ico = {'this':u'\uf07c', 'dir':u'\uf07b', 'file':u'\uf15b', 'link':u'\uf35d'}
ftype_ico = {'.py': u'\uf3e2', '.pyc': u'\uf3e2', '.doc': u'\uf1c2', '.docx': u'\uf1c2', '.docm': u'\uf1c2', '.odt': u'\uf1c2', 
			'.pdf': u'\uf1c1', '.zip': u'\uf1c6', '.tar': u'\uf1c6', '.7z': u'\uf1c6', '.key': u'\uf084', 
			'.cur': u'\uf245', '.sh': u'\uf1c9', '.md': u'\uf60f', '.gitignore': u'\uf841', 'git': u'\uf1d3', 
			'.AppImage': u'\uf5ba', '.Appimage': u'\uf5ba', '.exe': u'\uf3ca', '.xml': u'\uf121', '.html': u'\uf121', 
			'.r': u'\uf4f7', '.R': u'\uf4f7', 'README': u'\uf4d5', 'js': u'\uf3b8'}
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

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("dir", default='.', help="directory you want to list")
	parser.add_argument("-1", action="store_true", default=False, help="list items on individual lines")
	parser.add_argument("-a", "--all", action="store_true", default=False, help="list all files and folders")
	parser.add_argument("-l", "--long", action="store_true", default=False, help="long listing with details")
	parser.add_argument("-r", "--recursive", action="store_true", default=False, help='recursively list all files and folders')
	args = parser.parse_args()
	
	fmt = '39;49'
	ico = u'\uf0c8'

	# print(glob.glob(args.dir))

	for dirs, subs, files in os.walk(args.dir):
		# print(f"{dirs=}, {subs=}, {files=}")

		fmt = type_fmt['this']
		ico = type_ico['this']
		print(f"\x1b[{fmt}m {ico} {dirs} \x1b[0m")
		
		fmt = type_fmt['file']
		ico = type_ico['file']
		for f in files:
			if not args.all and f.startswith('.'):
				continue
			fico = ico
			ffmt = fmt
			if (os.path.islink(f)):
				fico = type_ico['link']
				ffmt = type_fmt['link']
			name, ext = os.path.splitext(f)
			if ext in ftype_ico:
				fico = ftype_ico[ext]
			elif name in ftype_ico:
				fico = ftype_ico[name]
			print(f"\x1b[{ffmt}m {fico} {f} ({os.path.splitext(f)})\x1b[0m")
		
		fmt = type_fmt['dir']
		ico = type_ico['dir']
		for s in subs:
			if not args.all and s.startswith('.'):
				continue
			fico = ico
			ffmt = fmt
			if s == ".git":
				fico = ftype_ico['git']
			print(f"\x1b[{ffmt}m {fico} {s} \x1b[0m")
		
		if not args.recursive:
			break
