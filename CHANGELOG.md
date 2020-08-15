# Changelog

## [Unreleased]

See [Milestones](https://github.com/sinus-x/rubbergoddess/milestones) to get an idea on what you can expect in the future.

- Feature [GH-163](https://github.com/sinus-x/rubbergoddess/issues/163): Compress database dumps
- Fix [GH-168](https://github.com/sinus-x/rubbergoddess/issues/168): Librarian: Remove trailing quote character
- Feature [GH-169](https://github.com/sinus-x/rubbergoddess/issues/169): Animals: Check if the avatar is still valid
- Feature [GH-170](https://github.com/sinus-x/rubbergoddess/issues/170): Errors: Print reason when cog fails to load
- Feature [GH-173](https://github.com/sinus-x/rubbergoddess/issues/173): Log reconnections
- Bug [GH-174](https://github.com/sinus-x/rubbergoddess/issues/174): Animals: Verified user is not sent to be checked
- Bug [GH-175](https://github.com/sinus-x/rubbergoddess/issues/175): Stalker: ?db remove crashes on len() called on int
- Bug [GH-177](https://github.com/sinus-x/rubbergoddess/issues/177): Faceshifter: Catch 404 errors on message fetch

### Developers

- `utils.paginate()`, so we don't have to cut messages to fit into 2000 char limit every time

### Maintenance

- Removed config key faceshifter/r2r_prefix ([GH-177](https://github.com/sinus-x/rubbergoddess/issues/177))
- Database dumps are compressed at the end of the month ([GH-163](https://github.com/sinus-x/rubbergoddess/issues/163))
- Altered text key errors/ExtensionFailed ([GH-170](https://github.com/sinus-x/rubbergoddess/issues/170))

## [1.0]

### Added

- Account cog: Manage bot's user account.
- Points cog: MEE6-like points.
- Seeking cog: Announce that you're seeking something/someone.

### Mods

- Actress response variables: `((mention))` and `((name))`

### Maintenance

- All cogs were moved to their separate directories, along with their strings and configuration. Manual transfer of config and text files is needed.

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



[Unreleased]: https://github.com/sinus-x/rubbergoddess/compare/v1.0.2...devel
[1.0]: https://github.com/sinus-x/rubbergoddess/compare/v0.6.1...v1.0.2
[0.6]: https://github.com/sinus-x/rubbergoddess/compare/v0.5.3...v0.6.1
[0.5]: https://github.com/sinus-x/rubbergoddess/compare/v0.4.2...v0.5.3
[0.4]: https://github.com/sinus-x/rubbergoddess/compare/v0.3.0...v0.4.2
[0.3]: https://github.com/sinus-x/rubbergoddess/compare/v0.2.2...v0.3.0
[0.2]: https://github.com/sinus-x/rubbergoddess/compare/v0.1.0...v0.2.2
[0.1]: https://github.com/sinus-x/rubbergoddess/releases/tag/v0.1.0
