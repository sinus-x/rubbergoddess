from sqlalchemy import Column, String, Integer
from repository.database import database

# 0 ... unknown
# 1 ... pending
# 2 ... verified
# 3 ... kicked
# 4 ... banned

class User(database.base):
	__tablename__ = 'users'

	login =      Column(String, primary_key=True)
	discord_id = Column(String)
	code =       Column(String)
	group =      Column(String)
	status =     Column(Integer, default=0)
	changed =    Column(String)
	comment =    Column(String)
