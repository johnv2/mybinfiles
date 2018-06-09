#!/bin/sh

USAGE="Usage: $0 host1 host2 host3 ... hostN"

if [ "$#" == "0" ]; then
	echo "$USAGE"
	exit 1
fi

while (( "$#" )); do
	#ssh root@$1 'if `ethtool eth4 | grep "Link detected" | grep -q yes` ; then for i in eth{0..3} ; do ifconfig $i down ; done ; fi

	ssh root@$1 'if `ethtool eth4 | grep "Link detected" | grep -q yes` ; then for i in eth{0..3} ; do ifconfig $i down ; done ; elif ! `ethtool eth4 | grep -q "No such device" 2>&1` ; then for i in eth{0..1} ; do ifconfig $i down ; done ; fi'

	shift
done
