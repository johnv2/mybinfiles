#!/bin/bash

ENVS="master
lower"

cd ~/apex/salt

for env in $ENVS
do
    git status
    echo "---"
    echo
done
