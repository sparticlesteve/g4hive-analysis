#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage:"
    echo "fetchResults.sh ORIGIN TARGET"
    exit 1
fi

origin=$1
target=$2

rsync -acv $origin/ $target
