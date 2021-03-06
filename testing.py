#!/usr/bin/python
'''
Created on Oct 4, 2010

@author: sam
'''
import pylights, time, kynetx, re, json
from pprint import pprint

p = pylights.plm("/dev/tty.serial") #,"verbose")
d = pylights.deviceFile("./devices.xml")
c = pylights.commandsFile("./commands.xml")

app = kynetx.kynetx("a41x138")

def showmessage(info, from_addr, command):
  print
  index = d.getIndexByAddress(from_addr)
  from_name = d.getNameByIndex(index)

  from_addr = re.sub('\s+','.',p.list_to_hex(from_addr))

  if from_name:
    print "got message from: " + p.list_to_hex(from_addr)
  else:
    from_name = "unknown"
    print "got message from: " + from_addr

  print "command hex: " + hex(command[0])
  command_name = c.getCommandFromHex(command[0])
  event_num = c.getCommandNumFromHex(command[0])
  if command_name:
    print "with command: " + command_name + " and event number: " + event_num

  directive = app.raise_event("insteon",command_name, {"number":event_num, "address":from_addr})

  for directive in app.directives:
    run_directive(directive)

p.addEventListener(showmessage);

def run_directive(directive_to_run):
  action = directive_to_run['action']
  if action == "fadein":
    address = directive_to_run['options']['address']
    p.fadeIn(address.encode('latin-1'))
  elif action == "fadeout":
    address = directive_to_run['options']['address']
    p.fadeOut(address.encode('latin-1'))
  elif action == "linktable":
    print "linked to:"
    pprint(p.getPlmLinkTable())
    print "\n"
  elif action == "monitor":
    p.startMonitorMode()
    p.addEventListener(showmessage)
  elif action == "link":
    linked = raw_input("enter the id of the responder: ")
    p.createLink("11.11.11","AA.AA.AA")

app.open_socket()
print app.get_token()
app.set_token("jamdev")
print app.get_token()


while(True):
  directives_string = app.get_socket_line();
  print directives_string
  directives = json.loads(directives_string)['query']['directive']
  app.parse_directives(directives)
  for directive in app.directives:
    run_directive(directive)
