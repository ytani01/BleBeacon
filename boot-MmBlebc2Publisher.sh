#!/bin/sh
#
# (c) 2020 Yoichi Tanibayashi
#
MYNAME=`basename $0`

BINDIR="${HOME}/bin"

VENV_DIR="${HOME}/env2-ble"
MACADDR="ac:23:3f:a0:08:ed"
TOKEN="token_VK8GQpDPFfDxZPGC"
CH="env1"
RES="temperature1 humidity1 battery1 msg1"

ACTIVATE_DO="${BINDIR}/activate-do.sh"
PUB_CMD="${BINDIR}/MmBlebc2Publisher.py"
PUB_OPT="-a 4"

LOGDIR="${HOME}/tmp"
LOGFILE="${LOGDIR}/env.log"

DATE_FMT="%Y/%m/%d %H:%M:%S"
ts_echo () {
    echo `date +"${DATE_FMT}"` $*
}

usage() {
    echo
    echo "  usage: ${MYNAME} venv_dir mac_addr token channel resouces"
    echo
}

ts_echo "> ${MYNAME}: start"

if [ ! -x ${ACTIVATE_DO} ]; then
    echo "${ACTIVATE_DO}: can not execute"
    exit 1
fi

if [ ! -x ${PUB_CMD} ]; then
    echo "${PUB_CMD}: can not execute"
    exit 1
fi

PID_PUB=`ps xw | grep python3 | grep ${PUB_CMD} | cut -d ' ' -f 2`
ts_echo "PID_PUB=${PID_PUB}"

if [ ! -z ${PID_PUB} ]; then
    ts_echo "< ${MYNAME}: end"
    exit 0
fi

if [ -f ${LOGFILE} ]; then
    mv -vf ${LOGFILE} ${LOGFILE}.1
fi

#
# wait IP up
#
ts_echo "wait IP addr .."
while [ `/sbin/ifconfig -a | grep inet | grep -v inet6 | grep -v 127.0.0 | wc -l` -eq 0 ]; do
    ts_echo ".."
    sleep 1
done

#
# restart bluetooth.service
#
ts_echo "restaret bluetooth.service .."
sudo systemctl restart bluetooth.service
sleep 2

#
# start publisher
#
ts_echo "start ${PUB_CMD} .."
${ACTIVATE_DO} ${VENV_DIR} ${PUB_CMD} ${PUB_OPT} ${MACADDR} ${TOKEN} ${CH} ${RES} > ${LOGFILE} 2>&1 &

ts_echo "< ${MYNAME}: end"
