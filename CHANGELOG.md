# Changelog
Development of this bot is quite chaotic. This document will try to document
the biggest changes, most importantly those that need some kind of edits to
configuration or database.

## [Unreleased]

See [Milestones](https://github.com/sinus-x/rubbergoddess/milestones) to get an idea on what you can
expect in the future.

### Added

- Judge cog: Replacement for Review
- Karma cog: Complete rewrite
- Meme: ?uwu
- Random: ?picsum
- Librarian: ?base64, ?hash
- Warden: Preventing useless reactions

### Removed

- Review cog

### Mods

- Errors are sent to stdout channel, botdef only recieves an error stub

### Developers

- Karma rewrite
- Reaction rewrite
- TODO `utils.remove_reaction(reaction, user)`
- self.embed(): footer parameter

### Maintenance

- Bumped reqired discord.py version to 1.3.4

## [0.4.0]

### Added

- Howto cog (data in `data/howto/howto.hjson`)

### Mods

- ?reverify command and Quarantine channel for reverifying (update your configuration files)

### Developers

- `Rubbercog.embed` function to make embed creation one-liner
- Removed `Rubbercog.throw*` functions
- Removed `Rubbercog.log` function

## [0.3.0]
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

## [0.2.0]
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


## [0.1.0]
Rubbergoddess detached from its parent project - [Rubbergod](https://github.com/Toaster192/rubbergod).

[Unreleased]: https://github.com/sinus-x/rubbergoddess/compare/v0.4.0...devel
[0.4.0]: https://github.com/sinus-x/rubbergoddess/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/sinus-x/rubbergoddess/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/sinus-x/rubbergoddess/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/sinus-x/rubbergoddess/releases/tag/v0.1.0
