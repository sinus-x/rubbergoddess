← Back to [home](index.md)

# Database

We're using PostgreSQL to store the data. Dump files differ between standalone and Docker version, but table schemes are the same.

Files for SQLAlchemy initialisation are saved in `repository/database`.

## Karma

**user_karma**

| name       | type       | attribute | default |
|------------|------------|-----------|---------|
| discord_id | BigInteger | primary   |         |
| karma      | Integer    |           | 0       |
| positive   | Integer    |           | 0       |
| negative   | Integer    |           | 0       |

**emote_karma**

| name     | type    | attribute | default |
|----------|---------|-----------|---------|
| emoji_ID | String  | primary   |         |
| value    | Integer |           | 0       |

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

| name       | type       | attribute  | default |
|------------|------------|------------|---------|
| discord_id | BigInteger | primary    |         |
| vote       | Boolean    |            | False   |
| review     | Integer    | reviews.id |         |

**subjects**

| name     | type   | attribute | default |
|----------|--------|-----------|---------|
| shortcut | String | primary   |         |
| category | String |           |         |
| name     | String |           |         |
| reviews  | Review |           |         |

## Verification

**users**

| name       | type       | attribute | default |
|------------|------------|-----------|---------|
| discord_id | BigInteger | primary   |         |
| login      | String     |           |         |
| code       | String     |           |         |
| group      | String     |           |         |
| status     | String     |           |         |
| changed    | String     |           |         |
| comment    | String     |           |         |

## Image

**images**

| name          | type       | attribute | default |
|---------------|------------|-----------|---------|
| attachment_id | BigInteger | primary   |         |
| message_id    | BigInteger |           |         |
| channel_id    | BigInteger |           |         |
| timestamp     | DateTime   |           |         |
| dhash         | String     |           |         |

## Points

**points**

| name    | type       | attribute | default |
|---------|------------|-----------|---------|
| user_id | BigInteger | primary   |         |
| points  | Integer    |           |         |

## Seeking

**seeking**

| name       | type       | attribute | default       |
|------------|------------|-----------|---------------|
| id         | Integer    | primary   | autoincrement |
| user_id    | BigInteger |           |               |
| channel_id | BigInteger |           |               |
| text       | String     |           |               |
| timestamp  | DateTime   |           |               |

← Back to [home](index.md)
