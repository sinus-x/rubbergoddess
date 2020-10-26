← Back to [module list](index.md) or [home](../index.md)

# Stalker

## ACL controlled commands

### guild

Display general information about guild and users.

### roleinfo (role)

Get information about role.

### channelinfo (channel)

Get information about channel.

### whois member (member)

Display database information about user. If the command is invoked in mod channel, everything in database is shown.

### whois login (login)

Search database for given login and see if person is registered on server.

### whois logins (prefix)

Search database for users where their login starts with prefix.

### database add (member) (email) (group)

Add entry to database, bypasing the verification.

### databse add-missing (member id) (email) (group)

Add member to databse, even if they are not present on the server.

### database remove (member) _(force)_

Remove member from database. If the "force" string is missing, display changes.

### database update (member) (key) (value)

Update user entry in database. See **users** table in  [database](../database.md) page.

### database show (parameter)

Show database entries. Parameter options: unverified, pending, kicked, banned.



← Back to [module list](index.md) or [home](../index.md)
