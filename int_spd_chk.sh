#!/bin/bash -
#title          :int_spd_chk.sh
#description    :Script designed to be used as a check_mk check which checks that interfaces are set to their maximum speed.
#author         :jdoshier
#date           :20150624
#version        :0.1
#requirements   :us
#usage          :./int_spd_chk.sh
#notes          :
#bash_version   :4.2.25(1)-release
#============================================================================

INTERFACES=$(/sbin/ifconfig | egrep -w "^eth[0-9]|^eth1[0-9]|^em[0-9]|^em1[0-9]|^p6p[0-9]|^p6p1[0-9]" | awk '{print $1}')
ETHTOOL=/sbin/ethtool
BADINTS=""

if [ -n "${INTERFACES}" ]
then
	for int in ${INTERFACES}
	do
		ETHTOOLOUT=$(${ETHTOOL} ${int})
		MAXSPEED=$(echo "${ETHTOOLOUT}" | grep -B 2 "Supports auto-negotiation:" | head -1 | grep -o [0-9]*)
		CURSPEED=$(echo "${ETHTOOLOUT}" | grep Speed | grep -o [0-9]*)

		# This catches interfaces with an "Unknown!" speed.
		if [[ -z "${MAXSPEED}" || -z "${CURSPEED}" ]]
		then
			BADINTS=${BADINTS}" ${int}"
			break
		fi

		# Our interfaces should be at least 1000 everywhere, if not we want to investigate.
		if [ "${MAXSPEED}" -lt 1000 ]
		then
			BADINTS=${BADINTS}" ${int}"
			break
		fi

		if [ "${CURSPEED}" -ne "${MAXSPEED}" ] 
		then
			BADINTS=${BADINTS}" ${int}"
		fi
	done

	if [ -n "${BADINTS}" ]
	then 
		echo "CRIT - Check speeds of following interface(s) -${BADINTS}"
		exit 2
	else
		echo "OK - All interfaces are at max speed"
		exit 0
	fi
else
	echo "CRIT - No eth/em/p6p interfaces found"
	exit 2
fi
