← Back to [module list](index.md) or [home](../index.md)

# Admin

## User commands

### commands

See command statistics since last start.

## Privileged commands

### system off (reason)

Owner only. In jail channel, remove write permission for @everyone and send a message explaining why the new users cannot be verified. Sends the message to bot spam channel, too.

### system on

Owner only. Restore write permission in jail channel, remove bot's message. Send message to bot spam channel that the bot is online again.

### system shutdown

Shutdown the bot.

### status

Mod only, mod room only. Display output from systemctl. Bot has to be run via systemctl service.

### journalctl

Mod only, mod room only. Display output from journalctl. Bot has to be run via systemctl service.

### config

Mod only. Display some information from config file, such as host machine, loader, logging level and extensions.


← Back to [module list](index.md) or [home](../index.md)
