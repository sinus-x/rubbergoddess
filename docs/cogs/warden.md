← Back to [module list](index.md) or [home](../index.md)

# Warden

Rubbergoddess checks attachments sent to defined channels. If there is a match with post in database, an warning embed is sent with link and percentage of similarity.

We are using [dhash](https://pypi.org/project/dhash/) to compute image hashes.

## User commands

This module has no commands usable by non-privileged users.

## Privileged commands

### scan history (limit)

Mod only. Limit is an integer or "all" string.

This command scans messages in current channel and adds their hashes to database.

### Performance

This was tested on VUT FIT server in june 2020.

- Command `?scan history 70900` was invoked at 12:22:32.
- Scanning started at 12:25:41.
- Scanning completed in 11 812 seconds (3:16:52, at 15:41:33) after scanning 21 375 hashes.
- Stats: 226MB RAM, 10 % CPU on their SU server.


← Back to [module list](index.md) or [home](../index.md)
