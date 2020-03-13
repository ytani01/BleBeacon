#!/bin/sh
#
# (c) 2020 Yoichi Tanibayashi
#
MYNAME=`basename $0`

VENV_DIR=$1
shift

echo $*

if [ -n ${VIRTUAL_ENV} ]; then
    deactivate
fi

cd ${VENV_DIR}
. ./bin/activate

