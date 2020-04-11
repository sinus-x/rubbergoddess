from sqlalchemy import Column, String, BigInteger
from repository.database import database

class User(database.base):
	__tablename__ = 'users'

	discord_id = Column(BigInteger, primary_key=True)
	login      = Column(String)
	code       = Column(String)
	group      = Column(String)
	status     = Column(String)
	changed    = Column(String)
	comment    = Column(String)
