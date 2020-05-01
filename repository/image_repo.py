from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.image import Image

class ImageRepository(BaseRepository):
	def add_image(self, discord_id: int, dhash: str, url: str):
		"""Add new image hash"""
		session.add(Image(discord_id=discord_id, dhash=dhash, url=url))
		session.commit()

	def getHash(self, dhash: str):
		return session.query(Image).filter(Image.dhash == dhash).all()

	def getLast(self, num: int):
		#TODO Return last X
		return

	def getAll(self):
		return session.query(Image)
