← Back to [module list](index.md) or [home](../index.md)

# Points

This is functionality inspired by [MEE6](https://mee6.xyz/leveling) discord bot. For every message, the user gains 15 - 25 points. This functionality has sixty second cooldown, so it is not simple message counter.

## User commands

### points me

Display your points score.

### points stalk (member)

Display points score for other member.

### points leaderboard

Display users with highest score.

### points loserboard

Display users with lowest score.

## Privileged commands

This module has no commands only usable by privileged users.

# Decrementing

In order to distinguish this from a simple activity counter, you can set up a cron script that will decrease the points in the given interval.

Because the database is password protected, you have to set the password elsewhere. We're gonna recommend the [`.pgpass` file](https://www.postgresql.org/docs/9.0/libpq-pgpass.html).

```bash
echo "<hostname>:<port>:<database>:<username>:<password>" > ~/.pgpass
chmod 0600 ~/.pgpass
```

In our production case, the string is `localhost:*:rubbergoddess:<username>:<password>`.

Then open the cron with `crontab -e` and add the entry:

```cron
0 0 * * * psql -U <username> -c "UPDATE points SET points=points*0.99;"
```

This will run the command every midnight and it will decrease all the points by 1%. This will lower the values by 7% in a week, 26% in a month or 60% in three months. It will prevent the most active users from keeping their points forever, they'll have to keep being active in order to stay on the top.

← Back to [module list](index.md) or [home](../index.md)
