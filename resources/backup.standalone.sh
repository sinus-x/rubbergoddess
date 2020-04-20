#!/bin/bash
mkdir -p ~/backups
pg_dump rubbergoddess > ~/backups/dump_`date +%Y-%m-%d"_"%H:%M:%S`.sql
exit 0
