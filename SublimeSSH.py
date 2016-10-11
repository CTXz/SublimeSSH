import sublime
import subprocess
import os

from sublime_plugin import WindowCommand, TextCommand, EventListener

## Global ##
local_dir = os.path.dirname(os.path.realpath(__file__))
home_dir  = "/home/%s" % os.popen('echo -n $(whoami)').read()
tempdir	  = "%s/.sublimeSSH" % home_dir

# Inteface/Client selection 
selectedInterface = None
interfaceList 	  = []
fileList		  = []

## Classes ##

# SSH #
class SSHInterface:
	remote_port		= 22

	remote_address  = None
	remote_user		= None
	remote_host  	= None
	remote_password = None

	# set
	#
	# Sets credentials for the SSH Interface instance
	#
	# Args:
	#	input : SSH address + password in the following format : [user@host password]
	def set(self, input):
		address 		= input.partition(" ")[0]
		password 		= input.partition(" ")[2]

		self.remote_address	 = address
		self.remote_user 	 = address.partition("@")[0]
		self.remote_host 	 = address.partition("@")[2]
		self.remote_password = password

	# ping
	#
	# Checks connection to remote host
	#
	# Returns :
	# 	On Success 				  	   : True
	# 	On Failure(Missing Application):-1
	# 	On Unavailable Connection 	   : False
	def ping(self):
		state = os.popen('sh %(1)s/ping.sh %(2)s %(3)s %(4)s' % {"1" : local_dir, "2" : self.remote_user, "3" : self.remote_host, "4" : self.remote_password}).read()
		
		if state == "1":
			print("Connection to %s established!" % self.remote_user)
			return True;

		elif state == "2":
			print("No ssh service installed!")
			return -1

		elif state == "3":
			print ("sshpass not installed!")
			return -1
		
		print("Connection to %s could not be established!" % self.remote_address)
		return False

	# pull
	#
	# Pulls/Transfers file from remote to local via scp
	#
	# Args:
	#	remote_path : Targeted file to pull from remote
	#	local_path  : File or Path to store transferred data on local machine
	#
	# Returns :
	#	On Successfull transfer : True
	#	On Failed transfer 		: False
	def pull(self, remote_path, local_path):
		if self.ping():
			if os.popen('sh %(1)s/pull.sh %(2)s %(3)s %(4)s %(5)s %(6)s' % {"1": local_dir, "2" : self.remote_user, "3" : self.remote_host, "4" : self.remote_password, "5" : remote_path, "6" : local_path}).read() == "1":
				return True
		return False

	# push
	#
	# Pushes/Transfers file from local to remote via scp
	#
	# Args:
	#	local_path:  Targeted file to push from local to remote
	#	remote_path: File or Path to store transferred data on remote machine	
	#
	# Returns :
	#	On Successfull transfer : True
	#	On Failed transfer 		: False
	def push(self, local_path, remote_path):
		if self.ping():
			if os.popen('sh %(1)s/push.sh %(2)s %(3)s %(4)s %(5)s %(6)s' % {"1": local_dir, "2" : self.remote_user, "3" : self.remote_host, "4" : self.remote_password, "5" : local_path, "6" : remote_path}).read() == "1":
				return True
		return False

# SSH File #
class SSHFile:
	def __init__(self, SSHInterface , path):
		self.remote_path = path
		self.ssh 		 = SSHInterface
		self.local_path  = "%(1)s/%(2)s/%(3)s%(4)s" % {"1" : tempdir, "2" : self.ssh.remote_host, "3" : self.ssh.remote_user, "4" : self.remote_path}

	window = None
	view = None

	# open
	# Opens the targeted remote SSH file inside the local sublime text editor
	#
	# Returns :
	#	On Success  : True
	#	On Fail		`: False
	def open(self):
		os.popen('mkdir -p %s' % os.path.dirname(self.local_path))
		if self.ssh.pull(self.remote_path, self.local_path):
			return True
		print("Unable to Open %s" % self.remote_path)
		return False

	# save
	# Saves local changes to the targeted remote SSH file
	#
	# Returns :
	#	On Success  : 1
	#	On Fail 	: 0
	def save(self):
		if os.path.isfile(self.local_path):
			if self.ssh.push(self.local_path, self.remote_path):
				return True
		print("%s could not be updated" % self.remote_path)	
		return 0

## Commands ##
class SshAddClientCommand(TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel("SSH Credentials", "user@host password", self.on_done_set, None, None)

	def on_done_set(self, input):
		interfaceList.append(SSHInterface())
		interfaceList[len(interfaceList) - 1].set(input)

		global selectedInterface
		if selectedInterface == None:
			selectedInterface = interfaceList[0]

		print("Client %s added" % (len(interfaceList) - 1))

class SshRemoveClientCommand(TextCommand):
	def run(self, edit):
		if selectedInterface != None:
			self.view.window().show_input_panel("Remove SSH Client", "", self.on_done_remove, None, None)
		else:
			print('No Clients available, please add clients via the "Add Client" command')

	def on_done_remove(self, input):
		if int(input) >= 0 and int(input) < len(interfaceList):
			interfaceList.pop(int(input))
			if len(interfaceList) == 0:
				selectedInterface = None
		else:
			print('Client %s does not exist! Please use the "List Clients" command to see a list of all available clients' % input)

class SshSetClientCommand(TextCommand):
	def run(self, edit):
		if selectedInterface != None:
			self.view.window().show_input_panel("Set SSH Client", "", self.on_done_set, None, None)
		else:
			print('No Clients available, please add clients via the "Add Client" command')			

	def on_done_set(self, input):
		if int(input) >= 0 and int(input) < len(interfaceList):						
			selectedInterface = interfaceList[int(input)]
			print("Switched to client %(1)s : %(2)s" % {"1" : input, "2" : selectedInterface.remote_address})
		else:
			print('Client %s does not exist! Please use the "List Clients" command to see a list of all available clients' % input)

# Set Current Client Credentials #
class SshSetCredentialsCommand(TextCommand):
	def run(self, edit):
		if selectedInterface != None:
			self.view.window().show_input_panel("SSH Credentials", "%s password" % selectedInterface.remote_address, self.on_done_set, None, None)
		else:
			print('No Clients available, please add clients via the "Add Client" command')

	# Split and sort address #
	def on_done_set(self, input):
		selectedInterface.set(input)

# Check Remote SSH Host Connection #
class SshPingCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			selectedInterface.ping()
		else:
			print('No Clients available, please add clients via the "Add Client" command')			

# Display SSH Credentials #
class SshDisplayCredentialsCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			print(selectedInterface.remote_user)
			print(selectedInterface.remote_host)
			print(selectedInterface.remote_password)
		else:
			print('No Clients available, please add clients via the "Add Client" command')

class SshListClientsCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			for interfaces in range(0, len(interfaceList)):
				print("%(1)s\t\t%(2)s" % { "1" : interfaces, "2" : interfaceList[interfaces].remote_address})
		else:
			print('No Clients available, please add clients via the "Add Client" command')

class SshOpenFileCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			self.window.show_input_panel("Open %s:" % selectedInterface.remote_address, "", self.on_done_open, None, None)
		else:
			print('No Clients available, please add clients via the "Add Client" command')

	def on_done_open(self, input):
		fileList.append(SSHFile(selectedInterface, input))
		if fileList[len(fileList) - 1].open():
			fileList[len(fileList) - 1].view   = self.window.open_file(fileList[len(fileList) - 1].local_path)
			fileList[len(fileList) - 1].window = fileList[len(fileList) - 1].view.window()

class SshSaveFileCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			for files in range(0, len(fileList)):
				if self.window.id() == fileList[files].window.id() and self.window.active_view().id() == fileList[files].view.id():
					fileList[files].save()
					break
		else:
			print('No Clients available, please add clients via the "Add Client" command')

def plugin_unloaded():
	os.popen('rm -r %s' % tempdir)