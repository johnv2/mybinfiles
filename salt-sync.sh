#!/bin/bash

ENVS="master
uat
stg
dev"

cd ~/salt

for env in $ENVS
do
    git checkout "$env" && git pull origin $env
    echo "---"
    echo
done
