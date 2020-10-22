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

R_DEPTH=0
PARENT=""

for args in "$@"
do
	if [ $args = "-a" ]
	then
		shopt -s dotglob
	elif [ ${args:0:2} = "-R" ]
	then
		R_DEPTH="${args:2}"
	fi
done


# args: $1 parentdir, $2 depth, $3 offset, $4 treebranch
function print_recur {
	for entry in "$1"*
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

		echo "$3 $4 ${ico} $entry"
		if [ -d $entry ] && [ $2 -gt 0 ]
		then
			echo "$3    |"
			print_recur "$entry/" "$(($2 - 1))" "$3   " "|"
		fi
	done
}

print_recur "$PARENT" "$R_DEPTH" ""
shopt -u dotglob
