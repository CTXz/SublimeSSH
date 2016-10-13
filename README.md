# Sublime Text 3 SSH Forwarding Plug-In

This is a simple SSH Plug-In for Sublime Text 3 that allows the user to edit remote SSH files straight from Sublime Text 3.
It support editing of mutiple files from even mutiple servers.

Please note that this Plug-In only supports Linux machines at the moment

## Installation
Before you install this Plug-In you will require the following tools for your Linux Distribtuion :
```
ssh
sshpass
```

Once the necessary tools/packages have been installed, you may go ahead and clone this repository into your Sublime Packages Directory.

## Usage

Using this Plug-In is fairly simple, for a full list of commands see the command section below.

Start out by creating a SSH Interface. This can be done using <b> ALT + SHIFT + A </b>

Sublime will the open an input panel below, this is where your SSH address and password comes in.

The syntax follows:
```
user@host password
```

Note that the passoword is <b> not hashed </b>! Set up the client with privacy!

Once you've set up your client, you may proceed opening a file by entering <b> ALT + SHIFT + O </b>

You'll be prompted with another input panel, this one will store the remote file you want to edit
If you've entered everything correctly, you'll be greeted with the file.

After editing the file you may save your changes by pressing <b> ALT + SHIFT + S </b>

If everything went right, the file will be updated successfully.

## Commands
To be done...
