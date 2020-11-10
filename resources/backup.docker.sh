#!/bin/bash

backups=~/backups

mkdir -p $backups
cd $backups

docker exec -it rubbergoddess_db_1 pg_dumpall -c -U postgres > dump_`date +%Y-%m-%d"_"%H:%M:%S`.sql

today=$(date +%d)

if [ $today -eq "01" ]; then
	# compress last month
	month=$(date -d "`date +%Y%m01` -1day" +%Y-%m)
	tar -cJf dump_$month.tar.xz dump_$month*
	rm dump_$month*
fi

exit 0
