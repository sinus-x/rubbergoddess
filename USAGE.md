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

**verify &lt;group&gt; &lt;xlogin00&gt;**

Request a security code. &lt;group&gt; is a privileged role ('FEKT', 'VUT' 
etc.), &lt;xlogin00&gt; is a VUT identifier.

**verify &lt;e-mail&gt;**

Request a security code. Used for non-VUT users.

If user submits e-mail from known university, they will be assigned a role 
(currently supported: 'MUNI', 'ČVUT', 'CUNI', 'VŠB').

**submit &lt;code&gt;**

Submit a security code. &lt;xlogin00&gt; is a VUT login or MUNI UČO, 
&lt;code&gt; is a security code from verification e-mail.

## KARMA cog

Karma cog contains code for karma and react-to-role functionality.

An emote can have positive, neutral or negative karma value. By reacting with 
an emote users can rate each other, to show their (dis)approval of a post.

React-to-role allows users independent management of selected roles (hobby 
channels), while still having control over core privileged roles.

**karma vote**

Admin only. Takes a server emote and creates a poll over emote's value.

**karma revote &lt;emote&gt;**

Admin only. Takes an emote and creates a poll over emote's value.

**karma give &lt;user&gt; &lt;value&gt;**

Admin only. Add karma to user.

**karma**

Show user's own karma.

**karma stalk &lt;user&gt;**

Show user's karma.

**karma get &lt;emote&gt;**

Get emote's value.

**karma message &lt;url&gt;**

Show total karma value of a message.

**leaderboard &lt;offset&gt;**

See karma leaderboard.

**bajkarboard &lt;offset&gt;**

See reversed karma leaderboard.

**givingboard &lt;offset&gt;**

See positive karma board.

**ishaboard &lt;offset&gt;**

See negative karma board.

## MEME cog

**on_message() listener**

- If 'uh oh' string is submitted by user, the bot says 'uh oh' too.
- 'PR': Send link to Github pull requests
- '🔧': Send link to Github issues
- '🔧👶': Send link to Github issues labeled as "good first issue"

**uhoh**

Say how many times the 'uh oh' triggered

**???**

Send one of question responses.

**hug &lt;user&gt;**

If no argument is specified, make the bot hug itself. Otherwise, hug mentioned 
user.

## RANDOM cog

**diceroll**

Roll a dice (check [the manual](https://wiki.roll20.net/Dice_Reference))

**pick &lt;opt0&gt; &lt;opt1&gt; [&lt;opts&gt;]**

Pick between entered (space separated) options

**flip**

Return true/false

**roll &lt;integer&gt; [&lt;integer&gt;]**

Pick a number in given interval. If only one argument is specified, pick 
between 0 and number.

## REVIEW cog

Allows to submit subject reviews, allowing for less formal notion compared to 
reviews in VUT's review system in it's IS.

**reviews add &lt;subject&gt; &lt;score&gt; [anonym] &lt;text&gt;**

Add a subject review. The subject must be declared in config file. The score is 
an integer between 0 and 4, 0 being the best.

**reviews remove &lt;subject&gt;**

Remove submitted review.

**reviews remove &lt;subject&gt; [id &lt;number&gt;]**

Admin only. Delete specified review.

**reviews &lt;subject&gt;**

See reviews for a given subject. 

## VOTE cog

**vote &lt;date&gt; &lt;time&gt; &lt;question&gt;**

Create a poll.

Format each poll option as `&lt;emote&gt; Description`

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

## STALKER cog

**whois &lt;discord id&gr;**

Fetch info from database.

**addUser &lt;discord id&gr; &lt;login&gt; &lt;group&gt;**

Add entry into database.

**deleteUser &lt;discord id&gt; [force]**

Remove entry from database. Use **force** to apply, simulate otherwise.

**comment &lt;discord id&gt; &lt;comment&gt;**

Add comment to user's database entry.

## FITWIDE cog

**find_rolehoarders [&lt;limit&gt;]**

Find users hoarding subject roles. Optional &lt;limit&gt; arguments specifies number 
of users to print.

**offer_subjects [&lt;group&gt;]**

Send a react-to-role message. Data are read from channel listing.

If no group is selected, prints all channels labeled as subject.

**purge &lt;channel&gt; [&lt;limit&gt;] [&lt;pinMode&gt;]**

Deletes messages from channel. If no limit is entered, all messages are delted.

If no pinMode is entered, pins are ignored. `pinStop` stops at pin, `pinSkip` 
skips the message.

**role_check (deprecated)**

_Mysterious, non-FIT rewrite needed._

**increment_roles (deprecated)**

Increment user roles.

_Non-FIT rewrite needed._

**get_users_login &lt;user&gt; (deprecated)**

Get user login information from database.

**get_logins_user &lt;user&gt; (deprecated)**

?

**reset_login &lt;login&gt; (deprecated)**

Remove login from database.

**connect_login_to_user &lt;login&gt; &lt;user&gt; (deprecated)**

Connect login with user.
