#!/bin/sh
#
# (c) 2020 Yoichi Tanibayashi
#
MYNAME=`basename $0`

DATE_FMT="%Y/%m/%d %H:%M:%S"
ts_echo () {
    echo `date +"${DATE_FMT}"` $*
}

while [ `/sbin/ifconfig -a | grep inet | grep -v inet6 | grep -v 127.0.0 | wc -l` -eq 0 ]; do
    ts_echo ".."
    sleep 1
done

IP_ADDR=`ifconfig | grep inet | grep -v inet6 | grep -v 127.0.0 | sed 's/^.*inet //' | cut -d ' ' -f 1`
ts_echo "IP_ADDR=${IP_ADDR}"
