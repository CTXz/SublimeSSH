# Copyright 2016 Patrick Pedersen <ctx.xda@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sublime
import subprocess
import os
import sublime_plugin

from sublime_plugin import WindowCommand, TextCommand, EventListener

## Global ##
local_dir = os.path.dirname(os.path.realpath(__file__))
home_dir  = "/home/%s" % os.popen('echo -n $(whoami)').read()
tempdir	  = "%s/.sublimeSSH" % home_dir

# Inteface/Client selection
selectedInterface = None
interfaceList     = []
fileList          = []

## Classes ##

# SSH #
class SSHInterface:
	remote_port     = 22

	remote_address  = None
	remote_user     = None
	remote_host     = None
	remote_password = None

	#Default Off
	timeout         = 0

	# set
	#
	# Sets credentials for the SSH Interface instance
	#
	# Args:
	#	input : SSH address + password in the following format : [user@host password]
	def set(self, input):
		address				 = input.partition(" ")[0]
		password			 = input.partition(" ")[2]

		self.remote_address	 = address
		self.remote_user	 = address.partition("@")[0]
		self.remote_host	 = address.partition("@")[2]
		self.remote_password = password

	# ping
	#
	# Checks connection to remote host
	#
	# Returns :
	# 	On Success                      : True
	# 	On Failure(Missing Application) :-1
	# 	On Unavailable Connection       : False
	def ping(self):
		state = os.popen('sh %(1)s/ping.sh %(2)s %(3)s %(4)s %(5)s' % {"1" : local_dir, "2" : self.timeout, "3" : self.remote_user, "4" : self.remote_host, "5" : self.remote_password}).read()

		if state == "1":
			print("Connection to %s established!" % self.remote_user)
			return True;

		elif state == "2":
			print("No ssh service installed!")
			return -1

		elif state == "3":
			print ("sshpass not installed!")
			return -1
		
		elif state == "0" and self.timeout == 0:
			print("Connection to %s could not be established!" % self.remote_address)
		else:
			print("Connection to %s could not be established! Timed out!" % self.remote_address)

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
	#	On Failed transfer      : False
	def pull(self, remote_path, local_path):
		if self.ping():
			if os.popen('sh %(1)s/pull.sh %(2)s %(3)s %(4)s %(5)s %(6)s %(7)s' % {"1" : local_dir, "2": self.timeout, "3" : self.remote_user, "4" : self.remote_host, "5" : self.remote_password, "6" : remote_path, "7" : local_path}).read() == "1":
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
	#	On Failed transfer      : False
	def push(self, local_path, remote_path):
		if self.ping():
			if os.popen('sh %(1)s/push.sh %(2)s %(3)s %(4)s %(5)s %(6)s %(7)s' % {"1": local_dir, "2": self.timeout, "3" : self.remote_user, "4" : self.remote_host, "5" : self.remote_password, "6" : local_path, "7" : remote_path}).read() == "1":
				return True
		return False

# SSH File #
class SSHFile:
	def __init__(self, SSHInterface , path):
		self.remote_path = path
		self.ssh 		 = SSHInterface
		self.local_path  = "%(1)s/%(2)s/%(3)s%(4)s" % {"1" : tempdir, "2" : self.ssh.remote_host, "3" : self.ssh.remote_user, "4" : self.remote_path}

	view = None

	# open
	# Opens the targeted remote SSH file inside the local sublime text editor
	#
	# Returns :
	#	On Success  : True
	#	On Fail     : False
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
	#	On Fail     : 0
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
			global selectedInterface					
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
			print("Timeout in s = %s" % selectedInterface.timeout)
		else:
			print('No Clients available, please add clients via the "Add Client" command')

class SshListClientsCommand(WindowCommand):
	def run(self):
		count = 0;
		if selectedInterface != None:
			for interfaces in interfaceList:
				print("%(1)s\t\t%(2)s" % { "1" : count, "2" : interfaces.remote_address})
				count += 1
		else:
			print('No Clients available, please add clients via the "Add Client" command')

class SshSetTimeoutCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			self.window.show_input_panel("Set Timeout in Seconds (0 to disable)", str(selectedInterface.timeout), self.on_done_set_timeout, None, None)
		else:
			print('No Clients available, please add clients via the "Add Client" command')			

	def on_done_set_timeout(self, input):
		selectedInterface.timeout = int(input)

class SshOpenFileCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			self.window.show_input_panel("Open %s:" % selectedInterface.remote_address, "", self.on_done_open, None, None)
		else:
			print('No Clients available, please add clients via the "Add Client" command')

	def on_done_open(self, input):
		fileList.append(SSHFile(selectedInterface, input))
		
		if fileList[len(fileList) - 1].open() == True:
			fileList[len(fileList) - 1].view = self.window.open_file(fileList[len(fileList) - 1].local_path)

class SshSaveFileCommand(WindowCommand):
	def run(self):
		if selectedInterface != None:
			if len(fileList) != 0:
				for file in fileList:
					if self.window.active_view().id() == file.view.id():
						self.window.run_command("save_all")
						file.save()
						break
			else:
				print("No SSH Files open!")
		else:
			print('No Clients available, please add clients via the "Add Client" command')

class SshCloseFilesCommand(WindowCommand):
	def run(self):
		for window in sublime.windows():
			for view in window.views():
				for SSHFile in fileList:
					if view.id() == SSHFile.view.id():
						window.focus_view(view)
						view.set_scratch(True)
						window.run_command("close_file")

class OnCloseSSHFile(sublime_plugin.EventListener):
	def on_pre_close(self, view):
		for SSHFile in fileList:
			if view.id() == SSHFile.view.id():
				fileList.remove(SSHFile)
				print("SSH File closed")

def plugin_unloaded():
	os.popen('rm -r %s' % tempdir)
	sublime.active_window().run_command ("ssh_close_files")