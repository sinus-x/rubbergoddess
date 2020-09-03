← Back to [module list](index.md) or [home](../index.md)

# ACL

This module manages access permissions for every command in the bot.

Upon execution, the command is looked up in the database. If it is not found, the execution is stopped and `False` is returned, failing the command check.

If the command has user override, the user is not checked for requred roles: It is directly allowed or denied. Bot's owner, defined in config with `admin_id`, is always allowed to execute commands; no checks are run against them.

As a starting point for group permissions, we try to map user's top role to ACL group. If the role ID is not linked to any group, then the second highest is used, and so on. The group permission has three possible values: **allow**, **disallow** and **not set**. If the group is allowed to run the command, the check function returns `True`, if the group prohibits users to run it, the function returns `False`.

If the group does not have behavior for given command set, then its parent group is used. If no group defines the outcome, the check returns function's default value.


You can see example group layout below. You can display yours with `?acl group list` command.
```
1  verify       693029899000000000
2    VUT        693032801000000000
3      FEKT     693032768000000000
5        MOD    693449479000000000
4    GUEST      693032851000000000
6      MUNI     740208696000000000
```

## User commands

This module has no commands usable by non-privileged users.

## Privileged commands

### acl group list

List ACL groups

### acl group add (name) (parent_id) (role_id)

Add new ACL group.

Set **parent_id** to **0**, if you don't want the group have any parents.

Set **role_id** to **0** if it's purpose is to act as parenting group for its children.

### acl group edit (id) (param) (value)

Edit ACL group. Param is **name**, **parent_id** or **role_id**, values are described above.

### acl group remove (identifier)

Remove ACL group. Parameter is group ID or name.

### acl rule get (command)

Display settings for given command.

### acl rule add (command)

Add command to database.

### acl rule remove (command)

Remove command from database.

### acl rule flush

Remove all commands. Useful if you plan to re-import the rules.

### acl user_constraint add (command) (discord_id) (allow)

Add command constraint. **discord_id** is user ID, **allow** is **True** (**true**, **1**) or **False** (**false**, **0**).

### acl user_constraint remove (constraint_id)

Remove command constraint.

### acl group_constraint add (command) (group) (allow)

Add command constraint. **group** is group ID or name, **allow** is **True**, **False** or **None**.

### acl group_constraint remove (constraint_id)

Remove command constraint.

### acl init

Load settings from file, located at `data/acl/commands.csv`.

The file may look like this:
```csv
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

Last column adds group overrides denying the access.

### acl audit

Print commands along with their default settings. Notifies if unsaved commands are found.

### acl check

Check if all commands have been saved to the database.


← Back to [module list](index.md) or [home](../index.md)
