← Back to [module list](index.md) or [home](../index.md)

# Stalker

## User commands

### guild

Display general information about guild and users.

## Privileged commands

### whois member (member)

Display database information about user. If the command is invoked in mod channel, everything in database is shown.

### whois login (login)

Elevated roles only. Search database for given login and see if person is registered on server.

### whois logins (prefix)

Elevated roles only. Search database for users where their login starts with prefix.

### database add (member) (email) (group)

Elevated roles only. Add entry to database, bypasing the verification.

### database remove (member) _(force)_

Elevated roles only. Remove member from database. If the "force" string is missing, display changes.

### database update (member) (key) (value)

Elevated roles only. Update user entry in database. See **users** table in  [database](../database.md) page.

### database show (parameter)

Elevated roles only. Show database entries. Parameter options: unverified, pending, kicked, banned.



← Back to [module list](index.md) or [home](../index.md)
