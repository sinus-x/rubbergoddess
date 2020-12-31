#!/bin/bash

backups=~/rubbergoddess-backups

mkdir -p $backups
cd $backups

pg_dump rubbergoddess > dump_`date +%Y-%m-%d"_"%H:%M:%S`.sql

today=$(date +%d)

if [ $today -eq "01" ]; then
	# compress last month
	month=$(date -d "`date +%Y%m01` -1day" +%Y-%m)
	tar -cJf dump_$month.tar.xz dump_$month*.sql
	rm dump_$month*.sql
fi

exit 0
