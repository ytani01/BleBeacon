#!/bin/sh
#
# (c) 2020 Yoichi Tanibayashi
#
MYNAME=`basename $0`

VENV_DIR=$1
shift

if [ -z "${VIRTUAL_ENV}" ]; then
    cd ${VENV_DIR}
    . ./bin/activate
fi

echo $VIRTUAL_ENV

cmdline=$*
echo $cmdline

exec $cmdline
