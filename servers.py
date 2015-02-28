#!/usr/bin/python

# Import external modules 
import snack
import pyrax
import keyring



#######################################################
# Snack form to get credential info from a user
#######################################################
def createServerForm(helpline, title, inptext):

  # Set up the main screen 
  credwin = snack.SnackScreen()

  # Set the help line
  credwin.pushHelpLine(helpline)
  
  # Get user entries
  ew = snack.EntryWindow(credwin, title, inptext,
                         ['Description:', 'Tenant:', 'Username:', 'API Key:'],
                         buttons = (("ok", "ok"), ("quit", "quit")),
                         entryWidth = 50)

  credwin.finish()

  # First array entry is the button, 2nd is a tuple of values
  status = ew[0]
  values = ew[1]

  # return the values if ok, 'quit' on quit
  if status == "ok":
    return values
  else:
    return status


##########################################################
# Display all of the credentials and return the selected
##########################################################
def listServers(helpline, title, servers):

  # Set up the main screen 
  mainlswin = snack.SnackScreen()

  # Set the help line
  mainlswin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 80, returnExit = 0)
  for server in servers:
    full = "<%s>: %s" % (server.id, server.name)
    li.append(full,server.id)

  bb = snack.ButtonBar(mainlswin, (("(o)k", "ok", 'o'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(mainlswin, title, 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  mainlswin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)



#########################################
# Display the primary credentials screen
#########################################
def mainServersScreen(helpline):


  # Set up the main screen 
  mainsrvwin = snack.SnackScreen()

  # Set the help line
  mainsrvwin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 40, returnExit = 0)
  li.append("l - List Servers", "server_list")
  li.append("a - Add Server", "server_add")
  li.append("d - Delete Server", "server_del")

  bb = snack.ButtonBar(mainsrvwin, (("(o)k", "ok", 'o'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(mainsrvwin, "Cloud Servers", 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  mainsrvwin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)



#######################################
# Main loop for the servers menus  
#######################################
def mainServersScreenLoop(help_text, selected_creds, curregion):

  # Set up pyrax to prepare for server actions
  print "Setting up Cloud Session..."
  pyrax.set_setting("identity_type", "rackspace")
  pyrax.set_setting("region", "ORD")
  cur_session = pyrax.create_context(
                            tenant_id = selected_creds[1], 
                            username = selected_creds[2],
                            api_key = selected_creds[3], 
                            verify_ssl=None) 
  cur_session.authenticate()
  srvobj = cur_session.get_client("compute", curregion)
  netobj = cur_session.get_client("network", curregion)

  # Start pulling some values to assist
  print "Pulling Server Objects..."
  myservers = srvobj.list()
  print "Pulling Image Objects..."
  myimages = srvobj.images.list()
  print "Pulling Flavor Objects..."
  myflavors = srvobj.flavors.list()
  print "Pulling Keypairs..."
  mykeypairs = srvobj.keypairs.list()
  print "Pulling Networks..."
  mynetworks = netobj.list()


  # call mainScreen
  while True:

    # Print the main servers screen
    ################################
    mcsrun = mainServersScreen(help_text)


    # Simple list the servers for the active datacenter 
    if mcsrun == "server_list":
      listServers(help_text, "Server List for %s" % curregion, myservers)

    # Return to the main menu with the results of cred actions
    if mcsrun == 'quit':
      return 

