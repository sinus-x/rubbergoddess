# Maintenance
## Database

If the bot runs inside Docker, you need to connect into the container shell first. 
With `docker ps -a` you should see a table (below, shortened):

```
CONTAINER ID   IMAGE                PORTS      NAMES
86632a710bd0   rubbergoddess_bot               rubbergoddess_bot_1
d2d2a3a2f4a2   postgres:12-alpine   5432/tcp   rubbergoddess_db_1
```

Execute `docker exec -it rubbergoddess_db_1 bash`.

CONNECT TO DATABASE

Note: When running directly, the values may be different.

```bash
psql -U postgres -p 5432
```

When connected, you can display all all databases with `\l`, all tables with `\dt` and use standard 
SQL queries like `SELECT * FROM bot_valid_persons;`.

BACKUP/RESTORE DATABASE

```bash
docker exec -it rubbergoddess_db_1 pg_dumpall -c -U postgres > dump_`date +%Y-%m-%d"_"%H-%M-%S`.sql
```

```bash
cat dump.sql | docker exec -it rubbergoddess_db_1 psql -U postgres
# or, more manually, to see if anything goes wrong
docker cp dump.sql rubbergoddess_db_1:dump.sql
docker exec -it rubbergoddess_db_1 bash
cat dump.sql | psql -U postgres
```


## SYSTEMD
_This next part assumes you have special user account `rubbergoddess`._

If you want to run the bot with systemd, copy `rubbergoddess.service` file into 
`/etc/systemd/system/rubbergoddess.service` and run it with 
`systemctl start rubbergoddess`.

If you want to grant `rubbergoddess` acount as little permissions as possible, 
you can use `visudo` and add the following entry:

```
Cmnd_Alias RGS = /bin/systemctl start rubbergoddess, /bin/systemctl stop rubbergoddess, /bin/systemctl restart rubbergoddess, /bin/journalctl -u rubbergoddess
rubbergoddess ALL=(ALL) NOPASSWD: RGS
```

`RGS` commands will be the only privileged ones the account can run.


