# Maintenance
## Database

If the bot runs inside Docker, you need to connect into the container shell first:

```bash
docker exec -it rubbergoddess_db_1 bash
```

CONNECT TO DATABASE

**Note**: When running standalone (without Docker), some parts may differ.

```bash
psql -U postgres -p 5432
```

When connected, you can display all all databases with `\l`, all tables with `\dt` and use standard 
SQL queries like `SELECT * FROM users;`.

BACKUP/RESTORE DATABASE

```bash
docker exec -it rubbergoddess_db_1 pg_dumpall -c -U postgres > dump_`date +%Y-%m-%d"_"%H-%M-%S`.sql
```

```bash
cat dump.sql | docker exec -it rubbergoddess_db_1 psql -U postgres
# or manually, to see if anything goes wrong
docker cp dump.sql rubbergoddess_db_1:dump.sql
docker exec -it rubbergoddess_db_1 bash
cat dump.sql | psql -U postgres
```

### Automatic backups

You can setup `cron` to execute the backup the database command every day:

_TODO_

**Note**: The database contains sensitive information (e-mails) and IS NOT encrypted. It is up to 
you to comply with the GDPR rules: limiting access to the server and/or encrypting.


## SYSTEMD
_This next part assumes you have special user account `rubbergoddess`._


Use the part that applies to your setup:
```bash
# Docker
cp rubbergoddess-docker.service /etc/systemd/system/rubbergoddess.service
systemctl start rubbergoddess
# Standalone
cp rubbergoddess-standalone.service /etc/systemd/system/rubbergoddess.service
systemctl start rubbergoddess
```

You may want to grant `rubbergoddess` account as little permissions as possible. 
Run `visudo` and add the following to the end of file:

```
Cmnd_Alias RGS = /bin/systemctl start rubbergoddess, /bin/systemctl stop rubbergoddess, /bin/systemctl restart rubbergoddess, /bin/journalctl -u rubbergoddess
rubbergoddess ALL=(ALL) NOPASSWD: RGS
```

`RGS` will be the only privileged commands the unprivileged `rubbergoddess` account can run.

