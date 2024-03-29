# Changelog

## Unreleased

- Backup: Various parser changes

## [1.5.1]

- ACL: Fix "acl rule get" embed
- Admin: "system shutdown" & "system restart" commands
- Animals: Detect reverts to default avatar
- Anonsend: Do not guard 'anonsend link' by ACL
- Anonsend: Add missing string
- Base: Fix pinning error while logging
- Base: Catch DM errors in bookmarks
- Librarian: Fix 'macaddress' throwing errors
- Meme: Include user avatar in 'relations' embed
- Roles: Fix react-to-role resolver when the line only has one word
- Roles: Alter react-to-role discovery
- Verify: Allow dash in e-mail

## [1.5.0]

- Core: Fix issues with embed creation, that were introduced by bumpting the library to version 1.7
- Core: Fix issues with user error reporting throwing errors
- ACL: Fix issues with corrputed imports
- Animals: Delay vote embed creation to combat Discord-side issues with content not being available at event creation
- Base: Prevent users from pinning system messages
- Comment: User comment module
- Karma: Limit "karma emoji" command to guild contexts
- Karma: Fix argument in "emoji" subcommand
- Librarian: Test "ipaddress" query with regex
- Random: Include explainxkcd.com link in "xkcd" command
- Random: Remove 50-character limit from "pick" output
- Stalker: Update the command API (argument can be Member, User or integer)
- Verify: Remove git hash from verification e-mail
- Verify: Various fixes to the e-mail logic

## [1.4.0]

### Added

- `dadjoke` command ([PR-261] by [nicx321])
- `Backup` cog
- Use Discord's replies
- `points` and `karma` user reply contains user's avatar
- Namedays are retrieved over HTTPS
- `Base`: The bot changes its status based on latency
- `Base`: Bookmark message by reacting with "🔖"
- `scan message` takes unlimited number of message links

### Updated

- Librarian properly displays the `week` command
- Animals module sends the user avatar when the vote is announced
- Animal updates are no longer logged as events
- Moved karma \*boards under the `karma` command as subcommands
- Warden has been rewritten to decrease maintenance complexity

## [1.3.0]

### Added

- Anonsend module

### Updated

- ACL has cleaner command interface and uses JSON files
- `review my-list` subcommand
- Check for `Admin`, so the #jail channel can't stay locked by accident

### Removed

- Howto module (not used, not mantained)

## [1.2.0]

First release of 2021 bumps the minor version, which sould have been done much earlier, probably.

### Updated

- Karma now also counts animated emojis
- Error notifications are no longer deleted
- `subject` and `role` commands removed
- Pinned-then-unpinned messages cannot be pinned again by the bot
- `review list` and `subject info` subcommands added

### Maintenance

- Added `points` degradation to the docs.

## [1.1.7]

### Added

- Meme: `bonk` command
- Base: Configuration for autopin that prevents pinning in selected channels

### Updated

- Meme: New animations for `pet`, `hyperpet` and `whip`

### Maintenance

- Database backup script has been updated: an error was deleting the new compressed archive
- Database scheme for meme interactions was redesigned. You'll have to drop the table and start anew (since the bot is not used elsewhere, I did not bother).

## [1.1.6]

### Added

- Random: The Cat API, The Dog API (`cat`, `dog`), `xkcd`
- Mover: Two commands to allow migrate old member account data to new one
- Librarian: `ipaddress` and `macaddress` commands

### Updated

- Mover also migrates member roles
- Shop code has been simplified

### Developers

- Moved `fetch_json()` to utils.py

## [1.1.5]

### Added

- Meme: `slap`, `spank` and `relations` commands
- Stalker: `db` commands only accept user ID

### Updated

- Voice: Working channel locking.
- Animals: Vote embed is not deleted; it's replaced by vote statistics.
- Points: Only official guilds are counter. Per-guild system is planned.
- `load`, `unload` and `reload` commands support multiple modules at the same time.

## [1.1.4]

### Added

- Meme: `pet` (ported from Rubbergod), `hyperpet`

### Updated

Because of API change, we're upgrading discord.py to 1.5. It's neccesary to enable Members intent on Discord Developers page.

### Developers

- `core/image_generator.py` has been renamed to `core/image_utils.py`.

## [1.1.3]

### Added

- Stalker: `roleinfo`, `channelinfo`

### Updated

- Systemd services. Manual `.service` file update is required -- follow instructions from the Wiki
- Librarian uses `aiohttp` to fetch information ([PR-214] by [LakshyaShastri])

### Maintenance

- Verify config keys `suffixes` and `constraints` now require underscore before them. Manual config adjustment is required.

## [1.1.2]

- Animals require Verify
- Verify deals with SMTP errors a bit better
- Fixed typo in Warden

## [1.1.1]

### Added

- Reviews are not limited to 1024 characters.
- `review add-anonymous`, because commands no longer work in DMs.
- `semester reset overwrites`
- `send dm`
- React-to-hide functionality
- `fish` command in Meme cog

### Updated

- Gatekeeper cog is renamed back to Verify
- Faceshifter cog is renamed to Roles
- Judge cog is renamed back to Review

### Maintenance

Some cogs were renamed, you'll have to alter your main config.

- Actress reactions require new boolean parameter `enabled`
- Actress countdown disables the reaction

## [1.1.0]

### Developers

- `utils.paginate()`, so we don't have to cut messages to fit into 2000 char limit every time

### Added

- ACL cog: Dynamic permission management
- Sync cog: Secondary guild management
- Semester cog: Semester-related management

## [1.0]

### Added

- Account cog: Manage bot's user account.
- Points cog: MEE6-like points.
- Seeking cog: Announce that you're seeking something/someone.

### Mods

- Actress response variables: `((mention))` and `((name))`

### Maintenance

- All cogs were moved to their separate directories, along with their strings and configuration. Manual transfer of config and text files is needed.
- Removed config key faceshifter/r2r_prefix
- Database dumps are compressed at the end of the month
- Altered text key errors/ExtensionFailed
- Removed Quarantine mechanics (too much confusion)
- Lot of fixes (see commits)

## [0.6]

### Added

- Animals cog: Elite club for users with animal avatar

### Developers

- `utils.remove_reaction(reaction, user)`
- `event.user()` and `event.sudo()` signatures changed

## [0.5]

### Added

- Judge cog: Replacement for Review
- Karma cog: Complete rewrite
- Meme: ?uwu
- Random: ?picsum
- Librarian: ?base64, ?hash
- Warden: Improved repost embed

### Removed

- Review cog

### Mods

- Errors are sent to stdout channel, botdev only recieves an error stub

### Developers

- Karma rewrite
- Reaction rewrite
- self.embed(): footer parameter

### Maintenance

- Bumped reqired discord.py version to 1.3.4

## [0.4]

### Added

- Howto cog (data in `data/howto/howto.hjson`)

### Mods

- ?reverify command and Quarantine channel for reverifying (update your configuration files)

### Developers

- `Rubbercog.embed` function to make embed creation one-liner
- Removed `Rubbercog.throw*` functions
- Removed `Rubbercog.log` function

## [0.3]
### Added
- Gatekeeper cog

### Removed
- Verify cog

### Mods
- `stdout` and `events` output text channels: duplicate for terminal stdout, user interaction.
These two replace previous logging channels, which weren't clearly defined.

### Developers
- Events class, used for event logging via `self.event.user()` and `self.event.sudo()`.
- Exceptions, handled inside of the cog.

### Maintenance
- Config: **HJSON** instead of **JSON**. Make sure you update the dependencies.
- Config: major naming change. Go line-by-line and copy values that apply.
- Actor: using word values (`full` instead of `F`, `text` instead of `T`)

## [0.2]
### Added
- Faceshifter cog (deprecating some of the code in `features/reaction.py`)

### Mods
- Change in pseudo-role naming:
  - `---FEKT` becomes `---PROGRAMMES`
  - `---` becomes `---INTERESTS`

### Developers
- United logging functions:

```
await self.[output|console].[debug..critical](source, message, exception)
```

### Maintenance
You need to update the database table `subjects`:

```sql
ALTER TABLE subjects
ADD COLUMN category VARCHAR,
ADD COLUMN name VARCHAR;
```

## [0.1]
Rubbergoddess detached from its parent project - [Rubbergod](https://github.com/Toaster192/rubbergod).


<!-- Releases -->

[Milestones]: https://github.com/sinus-x/rubbergoddess/milestones
[Unreleased]: https://github.com/sinus-x/rubbergoddess/compare/v1.5.1...devel
[1.5.1]: https://github.com/sinus-x/rubbergoddess/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/sinus-x/rubbergoddess/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/sinus-x/rubbergoddess/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/sinus-x/rubbergoddess/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.7...v1.2.0
[1.1.7]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.6...v1.1.7
[1.1.6]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.5...v1.1.6
[1.1.5]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.4...v1.1.5
[1.1.4]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/sinus-x/rubbergoddess/compare/v1.0.3...v1.1.0
[1.0]: https://github.com/sinus-x/rubbergoddess/compare/v0.6.1...v1.0.3
[0.6]: https://github.com/sinus-x/rubbergoddess/compare/v0.5.3...v0.6.1
[0.5]: https://github.com/sinus-x/rubbergoddess/compare/v0.4.2...v0.5.3
[0.4]: https://github.com/sinus-x/rubbergoddess/compare/v0.3.0...v0.4.2
[0.3]: https://github.com/sinus-x/rubbergoddess/compare/v0.2.2...v0.3.0
[0.2]: https://github.com/sinus-x/rubbergoddess/compare/v0.1.0...v0.2.2
[0.1]: https://github.com/sinus-x/rubbergoddess/releases/tag/v0.1.0

<!-- PRs and user links -->

[PR-214]: https://github.com/sinus-x/rubbergoddess/pull/214
[PR-261]: https://github.com/sinus-x/rubbergoddess/pull/261
[LakshyaShastri]: https://github.com/LakshyaShastri
[nicx321]: https://github.com/nicx321
