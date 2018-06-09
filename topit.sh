#!/bin/bash

export COLUMNS=160

OUTBASEDIR=/alldata/data/topit
OUTBASEFILE=topit

OUTFILE=${OUTBASEDIR}/${OUTBASEFILE}

SLEEP=60

usage="\
Usage: $(basename $0)\n \
	[--help]\n \
	[--interval <seconds between top runs, default is ${SLEEP}>]"

while [ ${1} ]
do
	case "${1}" in
	--help*|-help)   # Help
		echo -e "${usage}" 1>&2;
		exit
		;;
	-i*|--interval) # interval
		shift;
		SLEEP=$1;
		;;
	*)      # Default - do nothing
		/bin/true;
		;;
	esac;
	shift;
done;

if [ ! -d ${OUTBASEDIR} ]; then
	/bin/mkdir -p ${OUTBASEDIR}
fi

while [ true ]; 
do 
	DATE="`/bin/date +'%y%m%d'`"
	( date; /usr/bin/top -b -c -n 1; ) >> ${OUTFILE}.${DATE} 
	sleep ${SLEEP}; 
done & 

