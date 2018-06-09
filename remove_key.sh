#!/bin/sh

updatedb

files="`locate known_hosts | grep -v /etc | grep -v /usr/local/source`"

while read line ; do
   for i in $files ; do
        sed -i "\_${line}_d" $i
   done
done
