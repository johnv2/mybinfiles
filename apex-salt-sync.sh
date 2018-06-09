#!/bin/bash

ENVS="master
lower"

cd ~/apex/salt

for env in $ENVS
do
    git checkout "$env" && git pull origin $env
    echo "---"
    echo
done
