#!/bin/sh
#
# (c) 2020 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`pwd`
GITNAME=`basename $MYDIR`
echo "MYNAME  = $MYNAME"
echo "MYDIR   = $MYDIR"
echo "GITNAME = $GITNAME"

BINDIR="${HOME}/bin"
if [ ! -d ${BINDIR} ]; then
    mkdir -pv ${BINDIR}
fi

LOGDIR="${HOME}/tmp"

if [ X${VIRTUAL_ENV} = X ]; then
    echo "You must use and activate venv."
    exit 1
fi
VENV_NAME=`basename ${VIRTUAL_ENV}`
echo "VENV_NAME = ${VENV_NAME}"
echo

##### main

# Python3 packages
if [ -f requirements.txt ]; then
    echo "Installing python packages .."
    pip3 install -r requirements.txt
fi

# bluepy capability
echo "sudo setcap .."
sudo setcap 'cap_net_raw,cap_net_admin+eip' ${VIRTUAL_ENV}/lib/python3.7/site-packages/bluepy/bluepy-helper
