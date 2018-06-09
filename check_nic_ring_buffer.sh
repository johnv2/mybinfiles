#!/bin/bash

for interface in `ifconfig -a|grep eth|awk '{print $1}'`
do
   RESULT=( $(ethtool -g $interface|grep 'RX:'|awk '{print $2}') )
   MAX=${RESULT[0]}
   CURRENT=${RESULT[1]}
   if [ "$MAX" == "$CURRENT" ]
   then
     echo "Max Buffer Set"
   else
     echo "Setting Buffer to Max"
     ethtool -G $interface rx $MAX
   fi
done
