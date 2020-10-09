# Changelog

## [Unreleased]

See [Milestones] to get an idea on what you can expect in the future.

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
[Unreleased]: https://github.com/sinus-x/rubbergoddess/compare/v1.1.4...devel
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
[LakshyaShastri]: https://github.com/LakshyaShastri
