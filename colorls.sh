#!/bin/bash

declare -A icons=( 
["dir"]=""
["file"]=""
["sh"]=""
["py"]="" 
["c"]=""
["cpp"]="ﭱ"
["R"]="R"
["java"]=""
["php"]=""
["js"]=""
["html"]=""
["json"]=""
["xml"]="謹"
["doc"]=""
["docx"]=""
["xls"]=""
["xlsx"]=""
["odt"]=""
["ppt"]=""
["pptx"]=""
["pdf"]=""
["zip"]=""
["tar"]=""
["gz"]=""
["7z"]=""

)

for entry in *
do
	ext_split="$entry"
	ext="${ext_split##*.}"
	ico="${icons[$ext]}"
	if [ "$ico" = "" ]
	then
		if [ -d $entry ]
		then
			ico="${icons["dir"]}"
		elif [ -e $entry ]
		then
			ico="${icons["file"]}"
		fi
	fi

	echo "${ico} $entry"
done
