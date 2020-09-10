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

### semester reset programmes

Remove all programme roles form users

← Back to [module list](index.md) or [home](../index.md)
