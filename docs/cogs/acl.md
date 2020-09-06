← Back to [module list](index.md) or [home](../index.md)

# ACL

This module manages access permissions for every command in the bot.

Upon execution, the command is looked up in the database. If it is not found, the execution is stopped and `False` is returned, failing the command check.

If the command has user override, the user is not checked for requred roles: It is directly allowed or denied. Bot's owner, defined in config with `admin_id`, is always allowed to execute commands; no checks are run against them.

As a starting point for group permissions, we try to map user's top role to ACL group. If the role ID is not linked to any group, then the second highest is used, and so on. The group permission has three possible values: **allow**, **disallow** and **not set**. If the group is allowed to run the command, the check function returns `True`, if the group prohibits users to run it, the function returns `False`.

If the group does not have behavior for given command set, then its parent group is used. If no group defines the outcome, the check returns function's default value.


You can see example group layout below. You can display yours with `acl group list` command.
```
1  verify       693029899000000000
2    VUT        693032801000000000
3      FEKT     693032768000000000
5        MOD    693449479000000000
4    GUEST      693032851000000000
6      MUNI     740208696000000000
```

## Free commands

This module has no commands that are callable by everyone.

## ACL controlled commands

### acl group list

List ACL groups.

### acl group get (name)

Get ACL group.

### acl group add (name) (parent) (role_id)

Add new ACL group.

**name** must match regex `[a-zA-Z-]+`.

Set **parent** to **\"\"**, if the group should be orphaned.

Set **role_id** to **0** if the group should not be mapped to Discord role.

### acl group edit (name) (param) (value)

Edit ACL group. Param is **name**, **parent** or **role_id**, values are described above.

### acl group remove (name)

Remove ACL group.

### acl rule get (command)

Display settings for given command.

### acl rule add (command) (allow)

Add command to database.

**allow** parameter is boolean describing the default allow/deny response.

### acl rule remove (command)

Remove command from database.

### acl rule default (command) (allow)

Set the default outcome for DM or when no group defines it.

### acl rule flush

Remove all commands. Useful if you plan to re-import the rules.

### acl user_constraint add (command) (user_id) (allow)

Add command constraint. **user_id** is user's Discord ID, **allow** is boolean.

### acl user_constraint remove (constraint_id)

Remove command constraint.

### acl group_constraint add (command) (group) (allow)

Add command constraint. **group** is group ID or name, **allow** is boolean.

### acl group_constraint remove (constraint_id)

Remove command constraint.

### acl audit

Print commands along with their default settings. Notifies if unsaved commands are found.

Note that currently all commands are tested, not just those controlled by ACL.

### acl check

Check if all commands have been saved to the database.

Note that currently all commands are tested, not just those controlled by ACL.

### acl init

Load recommended settings from file, located at `data/acl/rules.csv`.

### acl import

Import your CSV file as an attachment. The file has to be called **rules.csv**.

The file may look like this:
```csv
command,default,allow,deny
verify,1,,VERIFY
hug,0,VERIFY,
load,0,,
acl rule get,0,MOD SUBMOD,
```

You can get much cleaner view if you open the file in LibreOffice Calc or Microsoft Excel:

| full command name | default result | allowed groups | forbidden groups |
|:------------------|----------------|:---------------|:-----------------|
| verify            | allow          |                | VERIFY           |
| hug               | deny           | VERIFY         |                  |
| load              | deny           |                |                  |
| acl rule get      | deny           | MOD SUBMOD     |                  |

Allowed groups is column representing ACL groups set to allow. If there are more than one, keep them space separated.

### acl export

Export current rules to file. User overrides are not exported.

← Back to [module list](index.md) or [home](../index.md)
