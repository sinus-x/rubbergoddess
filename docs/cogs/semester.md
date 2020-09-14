← Back to [module list](index.md) or [home](../index.md)

# Semester

## Free commands

This module has no commands that are callable by everyone.

## ACL controlled commands

### semester init subjects (channel)

Send react-to-role messages to given channel. List is read from guild channels, subject has to be in database.

### semester init programmes (channel) (category) (zeroes)

Send react-to-role messages to given channel. Category is `bachelor` or `master` or something else, depending on your setup. Zeroes is a boolean: if `True`, extra option is added for new users, that will be first-years next semester.

Data are read from file `data/semester/programmes.hjson`. Example:

```json
[
	{
		"name": "AUDIO INŽENÝRSTVÍ - Zvuková produkce a nahrávání",
		"type": "bachelor",
		"code": "AUDB-ZVUK",
		"years": 3
	},
	{
		"name": "AUDIO INŽENÝRSTVÍ - Zvuková technika",
		"type": "bachelor",
		"code": "AUDB-TECH",
		"years": 3
	},
	{
		"name": "ELEKTROTECHNIKA, ELEKTRONIKA, KOMUNIKAČNÍ A ŘÍDÍCÍ TECHNIKA - Telekomunikační a informační technika",
		"type": "master",
		"code": "M1-TIT",
		"years": 2
	},
	{
		"name": "INFORMAČNÍ BEZPEČNST",
		"type": "master",
		"code": "V-IBP",
		"years": 2
	}
]
```

### semester reset subjects

Remove overwrites from all subject channels

### semester reset overwrites (channel)

Remove overwrites from single text channel

### semester reset programmes

Remove all programme roles form users

## HOW TO: Guide to semester bump

The goal is not to cause any damage and prevent any problems from desynchronisation.

- [ ] Disable verification
- [ ] Update Gatekeeper's welcome message, if needed
- [ ] Remove `read messages` permission in the #add-subjects, #add-programme channels
- [ ] Update Faceshifter's `r2h_channels`, if needed (#add-programme)
- [ ] **semester reset subjects** (~10 minutes)
- [ ] Optional: Unload Sync
- [ ] **semester reset programmes** (~10 minutes)
- [ ] Optional: Load Sync
- [ ] **semester init subjects #add-subjects** (3 minutes)
- [ ] **semester init programmes #add-programme bachelor False** (2 minutes)
- [ ] Return permissions in given channels
- [ ] Enable verification

There is significant lag when you `init` reaction channels. The bot has to add reactions to the messages, which takes time. Then the internal cache probably needs flushing: it takes several minutes before reacting adds role or channel overwrite.

_It should all be finished within 30 minutes, if everything goes well. It all depends on how many members and roles you have; time information above are based on data from september 2020: little above 1000 members (over 700 of them able to self-assign programmes), 200 subject channels and 45 programme roles. The bot run on Raspberry Pi 3B+: hardware is not the limit here, Discord API is._

← Back to [module list](index.md) or [home](../index.md)
