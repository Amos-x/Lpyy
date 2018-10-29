#!/bin/bash
#

basedir=$(cd `dirname $0`; pwd)
cd $basedir/../apps

for d in $(ls);do
    if [ -d $d ] && [ -d $d/migrations ];then
        rm -f $d/migrations/00*
    fi
done

