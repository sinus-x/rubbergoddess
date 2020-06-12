# Changelog
Development of this bot is quite chaotic. This document will try to document
the biggest changes, most importantly those that need some kind of edits to
configuration or database.

## [Unreleased]
### Added
- Gatekeeper cog

### Removed
- Verify cog

### Mods
- `stdout` and `events` output text channels: duplicate for terminal stdout, user interaction.
These two replace previous logging channels, which weren't clearly defined.

### Developers
- Events class, used for event logging via `self.event.user()` and `self.event.sudo()`.

### Maintenance
- Config: **HJSON** instead of **JSON**. Make sure you update the dependencies.
- Config: major naming change. Go line-by-line and copy values that apply.

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

[Unreleased]: https://github.com/sinus-x/rubbergoddess/compare/v0.2.0...devel
[0.2.0]: https://github.com/sinus-x/rubbergoddess/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/sinus-x/rubbergoddess/releases/tag/v0.1.0
