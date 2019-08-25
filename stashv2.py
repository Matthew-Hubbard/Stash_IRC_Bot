#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import socket, ssl
import time
import yaml

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "iss.cat.pdx.edu" # Server
channel = "#Robots" # Channel
botnick = "moustache" # Bots nick
adminname = "Arctic" #admin IRC nickname
exitcode = "shave " + botnick #Text that we will use
yaml_filepath = "/stash/webstuff/quotas/stashes.yaml"
stash_filepath = "/stash/webstuff/quotas/quotas.stash"
delay = 0.6

s.connect((server, 6697)) # Connect to the server using the port 6667
ircsock = ssl.wrap_socket(s)
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n")) # user information
ircsock.send(bytes("NICK "+ botnick +"\n")) # assign the nick to the bot

def joinchan(chan): # join channel(s).
  ircsock.send(bytes("JOIN "+ chan + " " + "catsonly" +"\r\n")) 
  ircmsg = ""
#  ircsock.send(bytes("JOIN "+ "#" + " " + "catsonly" +"\r\n")) 
  ircmsg = ""
  while ircmsg.find("End of /NAMES list.") == -1: 
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

def ping(): # respond to server Pings.
  ircsock.send(bytes("PONG :pingis\n"))

def sendmsg(msg, target=channel): # sends messages to the target.
  #With this we are sending a ‘PRIVMSG’ to the channel. The ":” lets the server separate the target and the message.
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n"))

#This is the function that will find the stash name from quotas.stash and output info
def display_stash(stash_name, target = channel):
    stashquotas = open(stash_filepath,"r") #makes a file object stashquotas opening file
    quotas = stashquotas.read()
    pos = quotas.lower().find(stash_name)
    if pos != -1:
        stash = quotas[pos:].splitlines()[0]
        stash = stash.split()
        if len(stash) == 10 and stash_name == stash[0]:
            #sendmsg("|" + nick + ":")
            #sendmsg("/////////////////")
            sendmsg("|Stash Name........ " + stash[0],target)
            time.sleep(delay)
            sendmsg("|Owner............. " + stash[8],target)
            time.sleep(delay)
            sendmsg("|Group............. " + stash[9],target)
            time.sleep(delay)
            sendmsg("|Server............ " + stash[1],target)
            time.sleep(delay)
            sendmsg("|Windows........... " + "\\\\stash.cecs.pdx.edu\\" + stash[0] + " (<-Probably)",target)
            time.sleep(delay)
            sendmsg("|Linux............. " + stash[2],target)
            time.sleep(delay)
            sendmsg(("|Soft Quota........ %s, %.2f GB" % (stash[4], (int(stash[4])/1024))),target)
            time.sleep(delay)
            sendmsg(("|Used (On Disk).... %s, %.2f GB" % (stash[5], (float(stash[4])/1024))),target)
            time.sleep(delay)
            sendmsg(("|Used (Real Size).. %s, %.2f GB" % (stash[6], (float(stash[6])/1024))),target)
            time.sleep(delay)
            sendmsg(" ",target)
            #sendmsg("/////////////////")
            return 1
        else:
            #sendmsg(nick + ": Couldn't find stash " + stash_name + ".",target)
            return 0
    else:
        #sendmsg(nick + ": Couldn't find stash " + stash_name + ".",target)
        return 0

def yaml_loader(filepath):
    """loads a yaml file"""
    with open(filepath, "r") as file_descriptor:
        data = yaml.load(file_descriptor)
    return data

def display_dict(dictionary, target = channel):
    for key, value in dictionary.iteritems():
        line = "|" + str(key) + ": "
        if isinstance(value, dict):
            display_dict(value, target)
        else:
            line += str(value) 
            time.sleep(delay)
            sendmsg(str(line), target)

def display_yaml(name, yaml_filepath, target = channel):
    stash_yaml = yaml_loader(yaml_filepath)
    if stash_yaml['stash'].has_key(name):
        sendmsg("Found in stashs.yaml...", target)
        sendmsg("|Stash name: " + name)
        display_dict(stash_yaml['stash'][name], target)
    else:
        sendmsg("Stash " + str(name) + " not found.", target)

def stache():
    sendmsg("        ___")
    sendmsg("    __///|\\\\\\__")
    sendmsg("   //////|\\\\\\\\\\\\")   
    sendmsg(" ")

def main():
  joinchan(channel)
  #Start infinite loop to continually check for and receive new info from server. This ensures our connection stays open. 
  #We don’t want to call main() again because, aside from trying to rejoin the channel continuously, you run into problems
  #when recursively calling a function too many times in a row. An infinite while loop works better in this case.
  while 1:
    #Receive information from the IRC server. IRC will send out information encoded in
    #UTF-8 characters so we’re telling our socket connection to receive up to 2048 bytes and decode it as UTF-8 characters. 
    #We then assign it to the ircmsg variable for processing.
    ircmsg = ircsock.recv(2048).decode("UTF-8")

    #This part will remove any line break characters from the string. If someone types in "\n” to the channel, it will
    #still include it in the message just fine. 
    #This only strips out the special characters that can be included and cause problems with processing.
    ircmsg = ircmsg.strip('\n\r')

    #Print the received information to your terminal.
    print(ircmsg)

    #Here we check if the information we received was a PRIVMSG. PRIVMSG is how standard messages
    #in the channel (and direct messages to the bot) will come in. 
    #Most of the processing of messages will be in this section.
    if ircmsg.find("PRIVMSG") != -1:
      #First we want to get the nick of the person who sent the message. Messages come in from from IRC in the format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
      #We need to split and parse it to analyze each part individually.
      name = ircmsg.split('!',1)[0][1:]
      #Above we split out the name, here we split out the message.
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      channel_msg = ircmsg.split(' ')[2]
      #Now that we have the name information, we check if the name is less than 17 characters.
      if len(name) < 17:
        if message.find('hi ' + botnick) != -1 or message.find('Hi ' + botnick) != -1:
            sendmsg("Hello " + name + ". Do you need something? I can stash: or I can stache:")
        if message[:6].find('stash:') != -1:
            command = message.split(':', 1)[1].strip()
            if command == 'help':
                sendmsg("stash: [name_of_stash] or stache: [anything]")
            if command != 'help' and command != 'stache' and command != 'shave':
                stash_name = command
                #display_stash(stash_name, name, channel_msg)
                if channel_msg == botnick:
                    if 0 == display_stash(stash_name, name):
                        display_yaml(stash_name, yaml_filepath, name)
                else:
                    if 0 == display_stash(stash_name):
                        display_yaml(stash_name, yaml_filepath)
            if command == 'stache':
                stache()
            if name.lower() == adminname.lower() and command == 'shave':
                sendmsg("moustache shaved... :'(")
                ircsock.send(bytes("QUIT \n", "UTF-8"))
                return
                
        if name.lower() == adminname.lower() and message.rstrip() == exitcode:
          #If we do get sent the exit code, then send a message (no target defined, so to the channel) saying we’ll do it, but making clear we’re sad to leave.
          sendmsg("moustache shaved... :'(")
          #Send the quit command to the IRC server so it knows we’re disconnecting.
          ircsock.send(bytes("QUIT \n", "UTF-8"))
          #The return command returns to when the function was called (we haven’t gotten there yet, see below) and continues with the rest of the script. 
          #In our case, there is not any more code to run through so it just ends.
          return
    #If the message is not a PRIVMSG it still might need some response.
    else:
      #Check if the information we received was a PING request. If so, we call the ping() function we defined earlier so we respond with a PONG.
      if ircmsg.find("PING :") != -1:
        ping()
#Finally, now that the main function is defined, we need some code to get it started.
main()
 
