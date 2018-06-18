class Team:
	def __init__(self, dmg=0, heal=0, cast=0, kills=0):
		self.dmg = dmg
		self.heal = heal
		self.casts = cast
		self.kills = kills


class Teamfight:
	"""Used to store data of a Teamfight in a Match"""
	def __init__(self):
		# Player is in teamfight
		self.is_in = False
		self.result = ""
		self.players = []
		self.radiant_team = Team()
		self.dire_team = Team()


class TMFPlayer:
	"""Used to store data of a Player in a Teamfight"""
	def __init__(self):
		self.hero_id = 0
		self.side = ""
		self.ability_uses = 0
		self.item_uses = 0
		self.kills = 0
		self.deaths = 0
		self.buyback = False
		self.damage = 0
		self.healing = 0
		self.gold_delta = 0
		self.xp_delta = 0
