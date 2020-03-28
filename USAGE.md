# Usage

This document attempts to describe cog functions.

## BASE cog

**uptime**

Sends uptime message

**week**

Tells if the current calender & study week is even or odd

**god (goddess, help)**

Displays embed with available commands

## VERIFY cog

Implements verification system. Requires some setting-up: a _#jail_ channel with 
RW permission for _@everyone_, and a _'VERIFY'_ role (or other, as specified in 
config file). Other channels on a server should only be visible with (at least) 
_'VERIFY'_ role. It is recommended to have RO channel _#jail-info_ visible only to 
users without _'VERIFY'_ role, so newcomers know what to do.

**getcode <class> <xlogin00>**

Request a security code. <class> is a role (_'FEKT'_, _'VUT'_ etc.), <xlogin00> 
is a VUT login or MUNI UČO.

**verify <xlogin00> <code>**

Submit a security code. <xlogin00> is a VUT login or MUNI UČO, <code> is a 
security code from verification e-mail.

## KARMA cog

Karma cog contains code for karma and react-to-role functionality.

An emote can have positive, neutral or negative karma value. By reacting with 
an emote users can rate each other, to show their (dis)approval of a post.

React-to-role allows users independent management of selected roles (hobby 
channels), while still having control over core privileged roles.

**karma vote**

Admin only. Takes a server emote and creates a poll over emote's value.

**karma revote <emote>**

Admin only. Takes an emote and creates a poll over emote's value.

**karma give <user> <value>**

Admin only. Add karma to user.

**karma**

Show user's own karma.

**karma stalk <user>**

Show user's karma.

**karma get <emote>**

Get emote's value.

**karma message <url>**

Show total karma value of a message.

**leaderboard <offset>**

See karma leaderboard.

**bajkarboard <offset>**

See reversed karma leaderboard.

**givingboard <offset>**

See positive karma board.

**ishaboard <offset>**

See negative karma board.

## MEME cog

**on_message() listener**

- If 'uh oh' string is submitted by user, the bot says it too.
- 'PR': Send link to Github pull requests
- '🔧': Send link to Github issues

**uhoh**

Say how many times the 'uh oh' triggered

**question (??)**

Send '?' response

**hug <user>**

If no argument is specified, make the bot hug itself. Otherwise, hug mentioned 
user.

## RANDOM cog

**diceroll**

Roll a dice (check [the manual](https://wiki.roll20.net/Dice_Reference))

**pick <opt0> <opt1> [<opts>]**

Pick between entered (space separated) options

**flip**

Return true/false

**roll <integer> [<integer>]**

Pick a number in given interval. If only one argument is specified, pick 
between 0 and number.

## REVIEW cog

Allows to submit subject reviews, allowing for less formal notion compared to 
reviews in VUT's review system in it's IS.

**reviews add <subject> <score> [anonym] <text>**

Add a subject review. The subject must be declared in config file. The score is 
an integer between 0 and 4, 0 being the best.

**reviews remove <subject>**

Remove submitted review.

**reviews remove <subject> [id <number>]**

Admin only. Delete specified review.

**reviews <subject>**

See reviews for a given subject. 

## VOTE cog

**vote <date> <time> <question>**

Create a poll.

Format each poll option as `<emote> Description`

## NAME_DAY cog

**svatek**

Check nameday in Czech republic.

**meniny**

Check nameday in Slovakia.

## KACHNA cog

**kachna**

FIT-specific. Deprecated; moved to [Grillbot](https://github.com/Misha12/GrillBot).

---

Functionalities below are mod/admin only.

## FITWIDE cog

**find_rolehoarders [<limit>]**

Find users hoarding subject roles. Optional <limit> arguments specifies number 
of users to print.

**role_check**

_Mysterious, non-FIT rewrite needed._

**increment_roles**

Increment user roles.

_Non-FIT rewrite needed._

**get_users_login <user>**

Get user login information from database.

**get_logins_user <user>**

?

**reset_login <login>**

Remove login from database.

**connect_login_to_user <login> <user>**

Connect login with user.

## ACL cog

The bot assumes that a server has a '---' role, which separates self-assignable 
(hobby) and self-unassignable (MOD, VUT etc) roles. Anything below a '---' role 
can be added by users themselves by react-to-role mechanics, roles above can 
only be assigned by privileged user or by the bot.