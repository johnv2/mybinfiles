#!/bin/bash

if [ $# -eq 0 ] ; then
  echo "Usage: "
  exit
fi

hostname=$1

DO_SCRIPT=~/bin/do_precise_to_lacp.sh

ssh root@$hostname 'bash -s' < $DO_SCRIPT
