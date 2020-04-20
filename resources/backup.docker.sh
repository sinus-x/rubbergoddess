#!/bin/bash
mkdir -p ~/backups
docker exec -it rubbergoddess_db_1 pg_dumpall -c -U postgres > ~/backups/dump_`date +%Y-%m-%d"_"%H:%M:%S`.sql
exit 0
