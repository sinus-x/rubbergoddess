# Usage

This document attempts to describe core functions.

## BASE cog

**uptime**

Sends uptime message

**week**

Tells if the current calender & study week is even or odd

**god (goddess, help)**

Displays embed with available commands

## VERIFY cog

Implements verification system. Requires some setting-up: a #jail channel with 
RW permission for @everyone, and a 'VERIFY' role (or other, as specified in 
config file). Other channels on a server should be visible only with at least 
'VERIFY' role. It is reccomended to have RO channel #jail-info visible only to 
users without 'VERIFY' role, so newcomers know what to do.

**getcode**

Request a security code. 

**verify**

Submit a security code from the e-mail.

## KARMA cog

## MEME cog

**on_message() listener**

- If 'uh oh' string is submitted by user, the bot says it too.
- 'PR': Send link to Github pull requests
- '🔧': Send link to Github issues

**uhoh**

Say how many times the 'uh oh' triggered

**question (??)**

Send '?' response

**hug**

If no argument is specified, make the bot hug itself. Otherwise, print hug emote
 beside the tagged users' handle

## RANDOM cog

**diceroll**

Roll a dice (check [the manual](https://wiki.roll20.net/Dice_Reference))

**pick**

Pick between entered (space separated) options

**flip**

Return true/false

**roll**

Pick a number

## FITWIDE cog

## ACL cog

The bot assumes that a server has a '---' role, which separates self-assignable 
(hobby) and self-unassignable (MOD, VUT etc) roles. Anything below a '---' role 
can be added by users themselves by react-to-role mechanics, roles above can 
only be assigned by privileged user or by the bot.

## REVIEW cog

Allows to submit subject reviews, allowing for less formal notion compared to 
reviews in VUT's review system in its IS.

**reviews add**

Add a review in format `?review add <subject> <score> <text>`. For an anonymous 
submission, use `?review add <subject> <score> anonym <text>`..

**reviews remove**

Allows user to take his review back. Admin can delete any review.

**reviews <subject>**

See reviews for a given subject.

## VOTE cog

**vote <date> <time> <question>**

Create a poll.

To add options, add an emote and a description to next line for every entry.

## NAME_DAY cog

**svatek**

Check nameday in Czech republic.

**meniny**

Check nameday in Slovakia.

## KACHNA cog

**kachna**

Deprecated and FIT-specific; moved to [Grillbot](https://github.com/Misha12/GrillBot).
