class Problem:
	"""
	Represents a problem found while processing text. See Instance.process().
	"""
	def __init__(self, description: str, kanji: str, userdata):
		"""
		Creates a new problem object. Only created by the Instance and not the user.
		:param description: A text describing the problem.
		:param kanji: The kanji the problem is related to. Can be None.
		:param userdata: The userdata given as an argument to Instance.process().
		"""
		self.description = description
		self.kanji = kanji
		self.userdata = userdata
