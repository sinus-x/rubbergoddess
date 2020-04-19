#!/bin/bash
cd /home/rubbergoddess
mkdir -p backups
pg_dump rubbergoddess > backups/dump_`date +%Y-%m-%d"_"%H:%M:%S`.sql
exit 0
