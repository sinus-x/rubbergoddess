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

Implements verification system. Requires some setting-up: a #jail channel with 
RW permission for @everyone, and a 'VERIFY' role (or other, as specified in 
config file). Other channels on a server should only be visible with (at least) 
'VERIFY' role. It is recommended to have RO channel #jail-info visible only to 
users without 'VERIFY' role, so newcomers know what to do.

**getcode &gt;class&lt; &gt;xlogin00&lt;**

Request a security code. &gt;class&lt; is a role ('FEKT', 'VUT' etc.), &gt;xlogin00&lt; 
is a VUT login or MUNI UČO.

**verify &gt;xlogin00&lt; &gt;code&lt;**

Submit a security code. &gt;xlogin00&lt; is a VUT login or MUNI UČO, &gt;code&lt; is a 
security code from verification e-mail.

## KARMA cog

Karma cog contains code for karma and react-to-role functionality.

An emote can have positive, neutral or negative karma value. By reacting with 
an emote users can rate each other, to show their (dis)approval of a post.

React-to-role allows users independent management of selected roles (hobby 
channels), while still having control over core privileged roles.

**karma vote**

Admin only. Takes a server emote and creates a poll over emote's value.

**karma revote &gt;emote&lt;**

Admin only. Takes an emote and creates a poll over emote's value.

**karma give &gt;user&lt; &gt;value&lt;**

Admin only. Add karma to user.

**karma**

Show user's own karma.

**karma stalk &gt;user&lt;**

Show user's karma.

**karma get &gt;emote&lt;**

Get emote's value.

**karma message &gt;url&lt;**

Show total karma value of a message.

**leaderboard &gt;offset&lt;**

See karma leaderboard.

**bajkarboard &gt;offset&lt;**

See reversed karma leaderboard.

**givingboard &gt;offset&lt;**

See positive karma board.

**ishaboard &gt;offset&lt;**

See negative karma board.

## MEME cog

**on_message() listener**

- If 'uh oh' string is submitted by user, the bot says 'uh oh' too.
- 'PR': Send link to Github pull requests
- '🔧': Send link to Github issues

**uhoh**

Say how many times the 'uh oh' triggered

**question (??)**

Send one of question responses.

**hug &gt;user&lt;**

If no argument is specified, make the bot hug itself. Otherwise, hug mentioned 
user.

## RANDOM cog

**diceroll**

Roll a dice (check [the manual](https://wiki.roll20.net/Dice_Reference))

**pick &gt;opt0&lt; &gt;opt1&lt; [&gt;opts&lt;]**

Pick between entered (space separated) options

**flip**

Return true/false

**roll &gt;integer&lt; [&gt;integer&lt;]**

Pick a number in given interval. If only one argument is specified, pick 
between 0 and number.

## REVIEW cog

Allows to submit subject reviews, allowing for less formal notion compared to 
reviews in VUT's review system in it's IS.

**reviews add &gt;subject&lt; &gt;score&lt; [anonym] &gt;text&lt;**

Add a subject review. The subject must be declared in config file. The score is 
an integer between 0 and 4, 0 being the best.

**reviews remove &gt;subject&lt;**

Remove submitted review.

**reviews remove &gt;subject&lt; [id &gt;number&lt;]**

Admin only. Delete specified review.

**reviews &gt;subject&lt;**

See reviews for a given subject. 

## VOTE cog

**vote &gt;date&lt; &gt;time&lt; &gt;question&lt;**

Create a poll.

Format each poll option as `&gt;emote&lt; Description`

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

**find_rolehoarders [&gt;limit&lt;]**

Find users hoarding subject roles. Optional &gt;limit&lt; arguments specifies number 
of users to print.

**role_check**

_Mysterious, non-FIT rewrite needed._

**increment_roles**

Increment user roles.

_Non-FIT rewrite needed._

**get_users_login &gt;user&lt;**

Get user login information from database.

**get_logins_user &gt;user&lt;**

?

**reset_login &gt;login&lt;**

Remove login from database.

**connect_login_to_user &gt;login&lt; &gt;user&lt;**

Connect login with user.

## ACL cog

The bot assumes that a server has a '---' role, which separates self-assignable 
(hobby) and self-unassignable (MOD, VUT etc) roles. Anything below a '---' role 
can be added by users themselves by react-to-role mechanics, roles above can 
only be assigned by privileged user or by the bot.