from tkinter import Tk, LabelFrame, Canvas, Label, Scale, Entry, TOP, LEFT
import socket
import threading
from random import randint
from time import sleep


class MainWindow:
	def __init__(self):
		self.window = Tk()
		self.window.title("Chat")
		self.window.geometry("815x425")
		self.window.resizable(width=False, height=False)
		self.window.configure(bg="#000")
		self.window.bind("<MouseWheel>", self.__mouse_wheel)

		frame = LabelFrame(self.window, padx=0, pady=0, borderwidth=0, bg="#000")
		frame.pack(side=TOP, anchor="w", fill="both", expand="yes")
		self.__text = [[i, "#fff"] for i in ["Welcome to the chat !", "Type '/help' to get a list of commands.", "--------------------", ""]]
		self.__previous = ""
		self.__screen = Canvas(frame, width=800, height=400, bg="#000", highlightthickness=0)
		self.__screen.pack(side=LEFT, anchor="n", padx=0, pady=0)
		self.__automatique_scrollbar = True
		self.__scrollbar = Scale(frame, orient="vertical", from_=0, to=0, resolution=1, length=400, sliderlength=400, showvalue=0, bd=0, highlightthickness=0, command=self.__update_scrollbar)
		self.__scrollbar.pack(side=LEFT, anchor="n", padx=0, pady=0)
		self.show()
		frame = LabelFrame(self.window, padx=0, pady=0, borderwidth=0, bg="#000")
		frame.pack(side=TOP, anchor="w", fill="both", expand="yes")
		Label(frame, text=">", font="Consolas 12", fg="#fff", bg="#000", justify="left").pack(side=LEFT, anchor="n", padx=0, pady=0)
		self.__entry = Entry(frame, width=88, font="Consolas 12", fg="#fff", bg="#000", insertbackground="#fff")
		self.__entry.pack(side=LEFT, anchor="n", padx=0, pady=0)
		self.__entry.bind("<Key>", self.__entry_key_down)

		self.window.mainloop()

	def __update_scrollbar(self, event):
		self.__automatique_scrollbar = False
		if self.__scrollbar.get() == len(self.__text)-26: self.__automatique_scrollbar = True
		self.show()

	def show(self):
		self.__screen.delete("all")
		for i in range (26):
			if (i+self.__scrollbar.get()) < len(self.__text):
				self.__screen.create_text(5, i*15, anchor="nw", font="Consolas 12", fill=self.__text[(i+self.__scrollbar.get())][1], text=self.__text[(i+self.__scrollbar.get())][0])
			else : break

	def __entry_key_down(self, event):
		if len(self.__entry.get()) > 200: self.__entry.delete(200, len(self.__entry.get()))
		if event.keysym == "Return": self.__message()
		elif event.keysym == "Up": self.__entry.insert("end", self.__previous)
		if len(self.__entry.get()) > 200: self.__entry.delete(200, len(self.__entry.get()))

	def __mouse_wheel(self, event):
		if event.delta > 0 and self.__scrollbar.get() > 0: self.__scrollbar.set(self.__scrollbar.get()-1)
		elif event.delta < 0 and self.__scrollbar.get() < int(self.__scrollbar["to"]): self.__scrollbar.set(self.__scrollbar.get()+1)

	def __message(self):
		global user
		global name
		global color
		entry = self.__entry.get().split()
		if len(entry) > 0 :
			if entry[0][0] == "/":
				if entry[0] == "/help":
					if len(entry) == 1:
						self.add_text([["", "#fff"]], False)
						commands_list = ["List of commands :",
										"/help -> show a list of commands",
										"/host -> host a discussion",
										"/connect 'host adress' -> connect to a discussion",
										"/lock 'True/False' -> lock/unlock the discussion",
										"/exit -> leave the discussion",
										"/kick 'user' -> kick a user",
										"/nickname 'nickname' -> choose a nickname",
										"/color 'color in hexadecimal' -> choose your color",
										"/cls -> clear screen",
										]
						self.add_text([[i, "#fff"] for i in commands_list], True)
					else:
						command_list = ["host", "connect", "lock", "exit", "kick", "nickname", "color", "cls"]
						if len(entry) == 2 and entry[1] in command_list :
							help_list = {"host" : "This command while start hosting on your computer and give you an adress that other users can use to connect on your discussion.",
										"connect" : "Enter the address of the host computer as a parameter and you while join the discussion.",
										"lock" : "You cannot use this command if you are not the chat host. If you set the lockout value to 'True', no one will be able to join the discussion.",
										"exit" : "This command allows you to leave a discussion.",
										"kick" : "Enter the user's nickname after the command, to kick it. If you kick someone, he will still be able to join the discussion by reconnecting.",
										"nickname" : "Enter the nickname you want after the command. Your nickname is displayed when you send a message to find out who sent this message.",
										"color" : "Your color is the color using when you send a message. You can choose a color in this list : red, orange, yellow, green, cyan, blue, purple, magenta, pink, brown, grey. Or you can use the hexadecimal code of the color you want (You cannot set all the three tints at a number less than 50 or greater than 205).",
										"cls" : "This command allows you to clear the screen.",
										}
							self.add_text([["", "#fff"], ["Help on '{}' command :".format(command_list[command_list.index(entry[1])]), "#fff"], [help_list[entry[1]], "#fff"]], True)
						else: self.add_text([["Unknow command.", "#fff"]], False)
				elif len(entry) == 1:
					if entry[0] == "/host":
						if user == None:
							user = Server(self)
							self.add_text([["Adress : {}".format(user.adress), "#fff"]], False)
						else: self.add_text([["You are already in a discussion.", "#fff"]], False)
					elif entry[0] == "/exit":
						if user != None:
							user.close()
							if user.type == "server": self.add_text([["You closed the discussion.", "#fff"]], False)
							else: self.add_text([["You left the discussion.", "#fff"]], False)
							user = None
						else: self.add_text([["You are not in a discussion.", "#fff"]], False)
					elif entry[0] == "/cls":
						self.__text = []
						self.__update_scrollbar(None)
					else: self.add_text([["Unknow command.", "#fff"]], False)
				elif len(entry) == 2:
					if entry[0] == "/connect":
						if user == None:
							user = Client(self)
							test_connection = user.connect(entry[1])
							if test_connection: self.add_text([["You have join {} discussion.".format(user.adress), "#fff"]], False)
							else:
								self.add_text([["You cannot join this discussion.", "#fff"]], False)
								try: user.client.close()
								except: ""
								user = None
						else: self.add_text([["You are already in a discussion.", "#fff"]], False)
					elif entry[0] == "/lock" and entry[1] in ["True", "False"]:
						if user != None and user.type == "server":
							user.lock = entry[1] == "True"
							self.add_text([["The chat lock has been changed to '{}'.".format(entry[1]), "#fff"]], False)
						else: self.add_text([["You must be a chat host to do this.", "#fff"]], False)
					elif entry[0] == "/kick":
						if user != None and user.type == "server": user.kick(entry[1])
						else: self.add_text([["You must be a chat host to do this.", "#fff"]], False)
					elif entry[0] == "/nickname":
						if len(entry[1]) <= 20:
							name = entry[1]
							if user != None and user.type == "client": user.send("nickname;{}".format(name))
							self.add_text([["Your nickname is now {}.".format(name), "#fff"]], False)
						else: self.add_text([["Your nickname must have a maximum of 20 characters.", "#fff"]], False)
					elif entry[0] == "/color":
						if color_is_valid(entry[1]):
							color = "#"+entry[1]
							if user != None and user.type == "client": user.send("color;{}".format(color))
							self.add_text([["Your color has been changed.", "#fff"]], False)
						else: self.add_text([["Invalid color code.", "#fff"]], False)
					else: self.add_text([["Unknow command.", "#fff"]], False)
				else: self.add_text([["Unknow command.", "#fff"]], False)
			else:
				if user == None: self.add_text([[name+" : "+" ".join(entry), color]], False)
				elif user.type == "server": user.send([name+" : "+" ".join(entry), color])
				elif user.type == "client": user.send("message;"+" ".join(entry))
			self.__previous = " ".join(entry)
			self.__entry.delete(0, len(self.__entry.get()))
			self.show()

	def add_text(self, text, space):
		for i in text:
			for j in range(len(i[0])//87+1): self.__text += [[i[0][j*87:(j+1)*87], i[1]]]
		if space: self.__text += [["", "#fff"]]
		if len(self.__text) > 1000: self.__text = self.__text[-1000:]
		if len(self.__text) > 26:
			if self.__scrollbar["sliderlength"] > 10: self.__scrollbar["sliderlength"] = 400/len(self.__text)*26
			self.__scrollbar["to"] = len(self.__text)-26
		else: self.__scrollbar["sliderlength"] = 400
		if self.__automatique_scrollbar: self.__scrollbar.set(int(self.__scrollbar["to"]))

class Server:
	def __init__(self, mainwindow):
		self.type = "server"
		self.__active = True
		self.mainwindow = mainwindow
		self.__list_clients = {}
		self.__id = 0
		self.lock = False
		self.adress = socket.gethostbyname(socket.gethostname())
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((self.adress, 5566))
		thread_connections = threading.Thread(target=self.__connections)
		thread_connections.start()

	def __connections(self):
		while True:
			try:
				self.server.listen(0)
				if not self.lock:
					client = self.server.accept()
					self.send(["A new user have joined the discussion.", "#fff"])
					self.__list_clients[self.__id] = [client[1], client[0], threading.Thread(target=lambda x=self.__id: self.__receive(x)), "User", "#fff"]
					data = self.__list_clients[self.__id][1].recv(1024)
					self.__list_clients[self.__id] += [data.decode("utf8").split(";")]
					self.__list_clients[self.__id][2].start()
					self.__id += 1
			except: break

	def __receive(self, id):
		while True:
			try:
				data = self.__list_clients[id][1].recv(1024)
				data = data.decode("utf8").split(";")
				if data[0] == "nickname": self.__list_clients[id][3] = "".join(data[1:])
				elif data[0] == "color": self.__list_clients[id][4] = "".join(data[1:])
				elif data[0] == "message": self.send([self.__list_clients[id][3]+" : "+"".join(data[1:]), self.__list_clients[id][4]])
			except:
				if self.__active:
					name = self.__list_clients[id][3]
					del self.__list_clients[id]
					self.send(["{} left the discussion.".format(name), "#fff"])
					break

	def send(self, mess):
		self.mainwindow.add_text([mess], False)
		mess = ("{};{}".format(mess[1], mess[0])).encode("utf8")
		for i in self.__list_clients :
			self.__list_clients[i][1].sendall(mess)
		self.mainwindow.show()

	def kick(self, user):
		valid = False
		for i in self.__list_clients:
			if self.__list_clients[i][3] == user:
				valid, user = True, i
				break
		if valid:
			self.__active = False
			self.__list_clients[user][1].sendall("kick".encode("utf8"))
			sleep(1)
			self.__list_clients[user][1].close()
			name = self.__list_clients[user][3]
			del self.__list_clients[user]
			self.send(["{} have been kick from the discussion.".format(name), "#fff"])
		else: self.mainwindow.add_text([["This user does not exist.", "#fff"]], False)

	def close(self):
		self.__active = False
		self.server.close()
		for i in self.__list_clients: self.__list_clients[i][1].close()

class Client:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		self.type = "client"
		self.__active = True
		self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	def connect(self, adress):
		self.adress = adress
		try:
			self.client.connect((adress, 5566))
			sleep(1)
			self.client.sendall(("nickname;{}".format(name)).encode("utf8"))
			self.client.sendall(("color;{}".format(color)).encode("utf8"))
			self.__thread = threading.Thread(target=self.__receive)
			self.__thread.start()
			return True
		except: return False

	def __receive(self):
		global user
		while True:
			try:
				data = self.client.recv(1024)
				data = data.decode("utf8").split(";")
				if data == ["kick"]: data = ["#fff", "You have been kick from the discussion."]
				self.mainwindow.add_text([["".join(data[1:]), data[0]]], False)
				self.mainwindow.show()
				if data == ["#fff", "You have been kick from the discussion."]:
					self.close()
					user = None
			except:
				if self.__active:
					self.mainwindow.add_text([["The host closed the discussion.", "#fff"]], False)
					self.mainwindow.show()
					user = None
					break

	def send(self, mess): self.client.sendall(mess.encode("utf8"))

	def close(self):
		self.__active = False
		self.client.close()

def color_is_valid(color):
	characters = "0123456789abcdef"
	valid = True
	for i in color:
		if not i in characters:
			valid = False
			break
	if valid:
		if len(color) == 6:
			sub_50 = sum([characters.index(color[i*2])*16+characters.index(color[i*2+1]) < 50 for i in range (3)])
			over_205 = sum([characters.index(color[i*2])*16+characters.index(color[i*2+1]) > 205 for i in range (3)])
			return sub_50 < 3 and over_205 < 3
		else: return False
	else: return False

def random_color():
	characters = "0123456789abcdef"
	color = "ffffff"
	while not color_is_valid(color): color = "".join([characters[randint(0, 15)] for i in range (6)])
	return "#"+color

user = None
name = "User"
color = random_color()

main_window = MainWindow()

if user != None: user.close()
