import time
import _thread
from tkinter import *
from tkinter import ttk

from parse_manager import ParseManager

WIDTH = 250
HEIGHT = 150
REQUESTS_PER_MINUTE = 60


def get_milli_time():
	return int(round(time.time() * 1000))


class Application():
	def __init__(self):
		# Init Parse Manager
		self.manager = ParseManager()
		# Setup UI with tkinter
		self.root = Tk()
		self.root.title("Super Pro Dota Scouter")
		self.root.minsize(width=WIDTH, height=HEIGHT)

		self.mainframe = ttk.Frame(self.root, width=WIDTH, height=HEIGHT, padding="4 4 12 12")
		self.mainframe.grid(column=3, row=0, sticky=(N, W, E, S))
		self.mainframe.columnconfigure(0, weight=1)
		self.mainframe.rowconfigure(0, weight=1)

		label = Label(self.mainframe, text="Parse type:")
		label.pack(anchor=W)

		self.var = IntVar()
		R1 = Radiobutton(self.mainframe, text="Player", variable=self.var, value=1)
		R1.select()
		R1.flash()
		R1.pack(anchor=W)

		R2 = Radiobutton(self.mainframe, text="Match", variable=self.var, value=2)
		R2.pack(anchor=W)

		label2 = Label(self.mainframe, text="PlayerID/MatchID list (Separate multiple IDs through commas):")
		label2.pack(anchor=W)

		self.idVar = StringVar()
		E1 = Entry(self.mainframe, bd=2, width="64", textvariable=self.idVar)
		E1.pack(anchor=W)

		B = Button(self.mainframe, text="Scout", command=self.parse)
		B.pack(anchor=S)

	# End

	def start(self):
		self.root.mainloop()

	def setup_parse(self):
		try:
			_thread.start_new_thread(self.parse, ())
		except:
			print("Unable to start a new thread. (setup_parse())")

	def parse(self):
		self.manager.prepare_parse(self.var.get(), self.idVar.get())

		try:
			while 1:

				count = 0
				last_time = time.time()

				if self.manager.done:
					print("Finished Parse. Idling...")
					sys.exit()

				elif count < REQUESTS_PER_MINUTE:
					self.manager.update()
					count += 1

					if last_time > time.time() - 60.0:
						count = 0

		except KeyboardInterrupt:
			print("Exiting...")
			sys.exit()


'''
# Old loop
		start = get_milli_time() + 1000 / UPDATES_PER_SECOND
		count = 0
		try:
			while self.manager.done is False:
				sleep_time = start - get_milli_time()
				if sleep_time < 0:
					count += 1
					self.manager.update()
					start = get_milli_time() + 1000 / UPDATES_PER_SECOND
					if count > UPDATES_PER_SECOND:
						count = 0
						self.manager.request_count = 0

		except KeyboardInterrupt:
			print("Exiting...")
			sys.exit()

		print("Finished Parse")
'''