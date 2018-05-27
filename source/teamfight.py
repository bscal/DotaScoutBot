class Teamfight:
	"""Used to store data of a Teamfight in a Match"""
	def __init__(self):
		self.is_in = False
		self.result = ""
		self.players = []

		self.r_dmg = 0
		self.r_heal = 0
		self.r_casts = 0
		self.r_kills = 0
		self.d_dmg = 0
		self.d_heal = 0
		self.d_casts = 0
		self.d_kills = 0


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
