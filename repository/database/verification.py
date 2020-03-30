from sqlalchemy import Column, String, Integer
from repository.database import database

# unknown - pending - verified - kicked - banned

class User(database.base):
	__tablename__ = 'users'

	login =      Column(String, primary_key=True)
	discord_id = Column(String)
	code =       Column(String)
	group =      Column(String)
	status =     Column(String)
	changed =    Column(String)
	comment =    Column(String)
