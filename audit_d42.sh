#!/bin/bash

IN=/tmp/d42_devices
OUT=/tmp/d42_audit
rm -f $OUT

#d42iq.py -f
d42iq.py -1 > $IN

while read line ; do
    echo "Pinging $line..."
    ping -c 1 -w 5 $line > /dev/null

    if [ "$?" -ne 0 ] ; then
        echo $line >> $OUT
    fi
done < $IN
