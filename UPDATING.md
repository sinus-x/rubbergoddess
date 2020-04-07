# Updating to Rubbergoddess v2

Database changes:

- users.discord_id is primary key with data type of biting
- users.group column is now called ____
- users.changed has format YYYY-mm-dd HH:MM:SS

Bot changes:

- Configuration is now stored in json file. Back up the `config.py`, as it will 
 be overwritten.
- 