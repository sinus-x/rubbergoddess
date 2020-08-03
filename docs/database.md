← Back to [home](index.md)

# Database

We're using PostgreSQL to store the data. Dump files differ between standalone and Docker version, but table schemes are the same.

Files for SQLAlchemy initialisation are saved in `repository/database`.

## Verification

**users**

| name       | type       | note    |
|------------|------------|---------|
| discord_id | BigInteger | primary |
| login      | String     |         |
| code       | String     |         |
| group      | String     |         |
| status     | String     |         |
| changed    | String     |         |
| comment    | String     |         |

## ACL

**acl_groups**

| name      | type       | note    |
|-----------|------------|---------|
| id        | Integer    | primary |
| parent_id | Integer    | `-1` represents no parent |
| name      | String     |         |
| role_id   | BigInteger | discord role ID |

**acl_rule**

| name     | type            | note         |
|----------|-----------------|--------------|
| id       | Integer         | primary      |
| command  | String          |              |
| guild_id | BigInteger      |              |
| users    | acl_role_users  | relationship |
| groups   | acl_role_groups | relationship |

**acl_rule_users**

| name       | type       | note         |
|------------|------------|--------------|
| id         | Integer    | primary      |
| rule_id    | Integer    | acl_rules.id |
| discord_id | BigInteger |              |
| allow      | Boolean    |              |

**acl_rule_groups**

| name     | type    | note          |
|----------|---------|---------------|
| id       | Integer | primary       |
| rule_id  | Integer | acl_rules.id  |
| group_id | Integer | acl_groups.id |
| allow    | Boolean |               |


## Karma

**user_karma**

| name       | type       | note    |
|------------|------------|---------|
| discord_id | BigInteger | primary |
| karma      | Integer    |         |
| positive   | Integer    |         |
| negative   | Integer    |         |

**emote_karma**

| name     | type    | note    |
|----------|---------|---------|
| emoji_ID | String  | primary |
| value    | Integer |         |

## Review

**reviews**

| name        | type            | attribute | default |
|-------------|-----------------|-----------|---------|
| id          | Integer         | primary   |         |
| discord_id  | BigInteger      |           |         |
| anonym      | Boolean         |           | True    |
| subject     | String          | subjects.shortcut | |
| tier        | Integer         |           | 0       |
| text_review | String          |           | None    |
| date        | Date            |           |         |
| relevance   | ReviewRelevance |           |         |

**review_relevance**

| name       | type       | attribute  |
|------------|------------|------------|
| discord_id | BigInteger | primary    |
| vote       | Boolean    |            |
| review     | Integer    | reviews.id |

**subjects**

| name     | type   | note    |
|----------|--------|---------|
| shortcut | String | primary |
| category | String |         |
| name     | String |         |
| reviews  | Review |         |

## Image

**images**

| name          | type       | note    |
|---------------|------------|---------|
| attachment_id | BigInteger | primary |
| message_id    | BigInteger |         |
| channel_id    | BigInteger |         |
| timestamp     | DateTime   |         |
| dhash         | String     |         |

## Points

**points**

| name    | type       | note    |
|---------|------------|---------|
| user_id | BigInteger | primary |
| points  | Integer    |         |

## Seeking

**seeking**

| name       | type       | note    |
|------------|------------|---------|
| id         | Integer    | primary |
| user_id    | BigInteger |         |
| message_id | BigInteger |         |
| channel_id | BigInteger |         |
| text       | String     |         |

← Back to [home](index.md)
