← Back to [home](../index.md) or [module list](index.md)

# Actress

Send messages and attachments as Rubbergoddess.

Use dynamic replies, so the bot can react to user's own messages. Note: Only the first reaction that matches a condition is triggered.

## User commands

This module has no commands usable by non-privileged users.

## Privileged commands

### send text (channel) (text)

Owner only. Send a text to given text channel.

### send image (channel) (path)

Owner only. Send an image to given text channel. That image has to be in module's directory; the best way to add images is to add them with **image download** command (see below).

### react list

Mod only. List registered dynamic replies.

### react usage

Mod only. Display usage for all replies since last start.

### react add (name)

Mod only. This command has special formatting, as each parameter has its own line.

| Parameter  | Required | Values                | Note |
|------------|----------|-----------------------|------|
| type       | yes      | text, image           |      |
| match      | yes      | full, start, end, any |      |
| sensitive  | yes      | true, false           |      |
| triggers   | yes      | _string(s)_           | If the string has spaces, enclose it in quotes |
| responses  | yes      | _string(s)_           | If the string has spaces, enclose it in quotes |
| users      | no       | _ID(s)_               | Space separated                                |
| channels   | no       | _ID(s)_               | Space separated                                |
| counter    | no       | _integer_             | Delete after number of invocations             |

Example command:

```
?react add uhoh
type text
match any
sensitive true
triggers "uh oh"
responses "uh oh"
```

If the text contains `{mention}`, it will be replaced with author's tag.

### react edit (name)

Mod only. Edit previously created reaction. Formatting is the same as for **react add**, no parameter is required.

### react remove (name)

Mod only. Remove existing reaction.

### image list

Owner only. List availabe images.

### image download (url) (filename)

Owner only. Download an image from HTTP(S) source.

### image remove (filename)

Owner only. Delete an image.

### image show (filename)

Owner only. Show given image. This is an alias for **send image (current channel) (filename)**.


← Back to [home](../index.md) or [module list](index.md)
