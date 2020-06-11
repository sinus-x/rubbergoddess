# Changelog
Development of this bot is quite chaotic. This document will try to document
the biggest changes, most importantly those that need some kind of edits to
configuration or database.

## [Unreleased]
### Added
- Verify e-mails in config.

E-mail domains are no longer hardcoded into the cog. See `verification` section
of the default configuration file.

### Mods

- New stdout channel: everything that is printed to stdout is also sent here.

### Maintenance
- Config uses **HJSON** instead of **JSON**. Make sure you update the dependencies.

This means that you have to rename your `.json` files to `.hjson`. JSON is a
subset of HJSON, so you do not need to do anything else. We hope that this will
improve the readibility of the config file, as HJSON supports commenting.

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
