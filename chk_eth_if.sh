#!/bin/bash

MYEUID=`id | awk -F= '{print $2}' | awk -F\( '{print $1}'`

if [ ${MYEUID} -ne 0 ]
then
        echo "This script must be run as root or via sudo as root, exiting."
        exit 2
fi

usage="\
Usage: $(basename $0)\n \
        [--help]\n \
        [--verbose <increase verbosity>]\n \
        [-a <alert/notify via email>]\n \
        EXAMPLE:\n\n \
        $0 [--verbose]\n";
 
while [ ${1} ]
do
        case "${1}" in
        --help*|-help)   # Help
                echo -e "${usage}" 1>&2;
                exit
                ;;
        -v*|--v*) # Set the debug flag
                VERBOSE=true;
                ;;
        -a*|--a*) # Set the alert flag
                ALERT=true;
                ;;
        *)      # Default - do nothing
                /bin/true;
                ;;
        esac;
        shift;
done;

if [ ${VERBOSE} ]; then
        echo "Running in verbose mode."
	echo
fi

if [ -e /usr/bin/lshw ]; then 
	MACHINETYPE="`lshw -quiet | sed -n '3p' | awk '{print $2}'`"
	if [ ${MACHINETYPE} == "Bochs" ]; then
	        if [ ${VERBOSE} ]; then
			echo "Machine is not a physical sever.  Exiting..."
		fi
		exit 
	fi
fi

SPEED1="Speed: 1000Mb/s"
SPEED2="Speed: 10000Mb/s"
DUPLEX="Duplex: Full";

HOST="`uname -n`"
TMPFILE=/tmp/ethtool.$$

#INTERFACES="` cat /proc/net/dev | grep eth | awk -F: '{print $1}'`"
INTERFACES="`/sbin/ifconfig | egrep -w "^eth[0-9] |eth1[0-9] " | awk '{print $1}'`"

ALERTGROUP="shelmstadter@peak6.com"

for interface in ${INTERFACES}
do 
	if [ ${VERBOSE} ]; then
		echo "Checking interface ${interface}:"
	fi

	COMMAND="/sbin/ethtool ${interface}"

        if [ ${VERBOSE} ]; then
		${COMMAND} | grep -B 11 "Link detected: yes"
		echo
	fi

	${COMMAND} | grep -B 11 "Link detected: yes" > ${TMPFILE}.${interface} 2>&1

	if [ $? -eq 0 ]; then

		egrep "${SPEED1}|${SPEED2}" ${TMPFILE}.${interface} > /dev/null 2>&1
		if [ $? -ne 0 ]; then
			echo "Host '${HOST}' interface ${interface} is NOT \"${SPEED1}\" or  \"${SPEED2}\"."
			if [ ${ALERT} ]; then
                           echo "Host '${HOST}' interface ${interface} is NOT \"${SPEED1}\" or  \"${SPEED2}\"." | mail -s "ALERT: Nic speed issue on `hostname -s`" $ALERTGROUP 
			fi
		fi

		grep "${DUPLEX}" ${TMPFILE}.${interface} > /dev/null 2>&1
		if [ $? -ne 0 ]; then
			echo "Host '${HOST}' interface ${interface} is NOT \"${DUPLEX}\"."
			if [ ${ALERT} ]; then
			   echo "Host '${HOST}' interface ${interface} is NOT \"${DUPLEX}\"." | mail -s "ALERT: Nic duplex issue on `hostname -s`" $ALERTGROUP
			fi
		fi

	else
	        if [ ${VERBOSE} ]; then
			echo -e "\tLink not detected."
			echo
		fi
	fi

	rm -f ${TMPFILE}.${interface}
done

