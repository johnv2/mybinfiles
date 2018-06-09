#!/bin/bash

if [ $# -ne 1 ];
then
    echo "Usage: $0 hostname"
    exit 1
fi

HOST=$1
DATE=$(date -d "yesterday 13:00 " '+%Y-%m-%d')

PATH1="/data/tickdb/output/$DATE/*option*nbbo*"
PATH2="/data/tickdb/output/$DATE/bars/30/*option*nbbo*"

PATH_OUTPUT1=$(ssh $HOST "ls $PATH1 2>/dev/null| wc -l")
PATH_OUTPUT2=$(ssh $HOST "ls $PATH2 2>/dev/null| wc -l")

if [ "$PATH_OUTPUT1" -gt 0 ] && [ "$PATH_OUTPUT2"  -gt 0 ];
then
    echo ""
    echo "We have option NBBO data for $DATE"
    echo $PATH_OUTPUT1
    echo $PATH_OUTPUT2
fi
