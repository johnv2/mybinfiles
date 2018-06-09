#!/bin/bash

if [ $# -eq 0 ] ; then
  echo "Usage: "
  exit
fi

hostname=$1

DO_SCRIPT=~/bin/do_serverbuild.sh
BCFG2_METADATA=~/bcfg2/Metadata

BCFG2_PROFILE=$(grep $hostname.peak6.net $BCFG2_METADATA/* | awk -F"'" '{print $2}')

sed -i s/BCFG2_PROFILE_HOLDER/$BCFG2_PROFILE/ $DO_SCRIPT

ssh root@$hostname 'bash -s' < $DO_SCRIPT

sed -i s/$BCFG2_PROFILE/BCFG2_PROFILE_HOLDER/ $DO_SCRIPT
