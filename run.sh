#!/bin/sh
app_path=$1
profile=$2
app_jar=backend/main.py

echo "app_path=$app_path"
echo "profile=$profile"

echo 'run app'
PID=`ps -ef | grep ${app_jar} | grep -v grep | awk '{print $2}'`
if [ ! $PID ]; then
  echo "应用不存在"
else
  echo "killing $PID"
  kill -9 $PID
fi

python3 -V

#nohup python3 ${app_path}/${app_jar} config-${profile}.ini > ${app_path}/start.log 2>&1 & sleep 1
#python3 ${app_path}/${app_jar} config-${profile}.ini > ${app_path}/start.log 2>&1 & sleep 2

python3 ${app_path}/${app_jar} -e ${profile} -p 8080

PID=`ps -ef | grep ${app_jar} | grep -v grep | awk '{print $2}'`
echo "start run ${app_jar} PID:${PID}"

#cat ${app_path}/start.log