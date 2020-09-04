#!/bin/bash

backups=~/backups

mkdir -p $backups
cd $backups

pg_dump rubbergoddess > dump_`date +%Y-%m-%d"_"%H:%M:%S`.sql

today=$(date +%d)

if [ $today -eq "1" ]; then
	# compress last month
	month=$(date -d "`date +%Y%m01` -1day" +%Y_%m)
	tar -cJf dump_$month.tar.xz dump_$month*
	rm dump_$month*
fi

exit 0
