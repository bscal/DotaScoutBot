from parse_manager import ParseManager
import sys
import time

DEBUG = True
# Opendota's only allows 1(5) request for free(with key)
UPDATES_PER_SECOND = 10
manager = ParseManager()


def get_milli_time():
	return int(round(time.time() * 1000))


def update():
	if manager.done:
		print("\nFinished.\nExiting...")
		sys.exit()
	else:
		manager.update()


def init_dota(args):
	""" Parses the arguments to setup whatever user needs.
		If you -match will set mode to matched
	"""
	content = []

	for arg in args:
		if "-" in arg:
			# Sets mode to match
			if arg == "-match":
				manager.type = "match"
				print("ParseMode set to match")
			elif arg == "-update":
				pass
			elif arg == "-pm":
				pass
		else:
			content.append(arg)

	manager.prepare_parse(content)


def main():
	start = get_milli_time() + 1000 / UPDATES_PER_SECOND
	count = 0

	init_dota(sys.argv[1:])

	try:
		while 1:
			sleep_time = start - get_milli_time()
			if sleep_time < 0:
				count += 1
				update()
				start = get_milli_time() + 1000 / UPDATES_PER_SECOND
				if count > UPDATES_PER_SECOND:
					count = 0
					manager.request_count = 0

	except KeyboardInterrupt:
		print("Exiting...")
		sys.exit()


if __name__ == "__main__":
	main()
