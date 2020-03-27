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
```
