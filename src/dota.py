import sys

from app import Application

DEBUG = True
app = None


def init_dota(args, app):
	""" Parses the arguments to setup whatever user needs.
		If you -match will set mode to matched
	"""
	content = []

	for arg in args:
		if "-" in arg:
			# Sets mode to match
			if arg == "-match":
				app.manager.type = "match"
				print("ParseMode set to match")
			elif arg == "-update":
				pass
			elif arg == "-pm":
				pass
		else:
			content.append(arg)

	app.manager.prepare_parse(content)


def update():
	pass


def main():
	global app
	app = Application()

	if len(sys.argv) > 1:
		init_dota(sys.argv[1:], app)

	app.start()


if __name__ == "__main__":
	main()
