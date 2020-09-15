← Back to [module list](index.md) or [home](../index.md)

# Actress

Send messages and attachments as Rubbergoddess.

Use dynamic replies, so the bot can react to user's own messages. Note: Only the first reaction that matches a condition is triggered.

## User commands

This module has no commands usable by non-privileged users.

## Privileged commands

### send text (channel) (text)

Owner only. Send a text to given text channel.

### send dm (user) (text)

Send direct message to specified user.

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
| enabled    | yes      | true, false           |      |

Example command:

```
?react add uhoh
type text
match any
sensitive true
triggers "uh oh"
responses "uh oh"
enabled true
```

The counter is decremented every time the reaction is invoked. When it reaches zero, the reaction is disabled.

If the text contains `((name))`, it will be replaced with author's nickname; `((mention))` will be replaced with author's tag.
_Note: Before the v1.0 version, the mention string was `{mention}`._

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


← Back to [module list](index.md) or [home](../index.md)
