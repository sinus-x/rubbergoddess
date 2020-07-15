← Back to [module list](index.md) or [home](../index.md)

# Gatekeeper

## User commands

### verify (e-mail)

Non-verified only, jail channel only. Send an verification code to supplied e-mail address. Users get their role from their e-mail, this link is saved in `gatekeeper/suffixes` config entry.

### reverify change (e-mail)

Quarantined only, quarantine or DM only. Change user's e-mail address (thus, their role).

_Note: This has not been fully tested in production._

### reverify prove

Quarantined only, quarantine or DM only. Send e-mail to user's address to prove they still have access to it.

_Note: This has not been fully tested in production._

### submit (code)

Submit user's verification code from recieved e-mail.

## Privileged commands

This module has no commands only usable by privileged users.


← Back to [module list](index.md) or [home](../index.md)
