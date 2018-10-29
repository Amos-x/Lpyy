#!/bin/bash
#

basedir=$(cd `dirname $0`; pwd)

python3 $basedir/../apps/manage.py loaddata init