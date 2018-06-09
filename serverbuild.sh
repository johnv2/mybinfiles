#!/bin/bash

if [ $# -eq 0 ] ; then
  echo "Usage: "
  exit
fi

hostname=$1

prep_serverbuild.sh $1 | mail -s "$1 server build" jdoshier@peak6.com
