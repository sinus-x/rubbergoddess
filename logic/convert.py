import string

class Convert:
	@staticmethod
	def emote_number_from_int (number):
		"""Convert number to emote"""
		numbers = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
		if number > len(numbers):
			return None
		return numbers[number]
  