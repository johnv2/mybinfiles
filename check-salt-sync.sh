#!/bin/bash

ENVS="master
dev
stg
uat"

cd ~/salt

for env in $ENVS
do
    git status
    echo "---"
    echo
done
