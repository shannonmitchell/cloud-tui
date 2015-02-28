#!/usr/bin/python

# Import external modules 
import snack
import pyrax
import keyring



#######################################################
# Snack form to get credential info from a user
#######################################################
def createServerForm(helpline, title, myservers, myimages, myflavors, mykeypairs, mynetworks): 

  # Set up the main screen 
  newsrvwin = snack.SnackScreen()

  # Set the help line
  newsrvwin.pushHelpLine(helpline)
  
  # Get user entries
  nametb = snack.Textbox(13,1,"Server Name: ",scroll=0,wrap=0) 
  namee = snack.Entry(50, text="", hidden = 0, password = 0, scroll = 1, returnExit = 0)

  # Allow Image Selection
  imagetb = snack.Textbox(13,1,"Image: ",scroll=0,wrap=0) 
  imagelb = snack.Listbox(height = 3, width = 50, returnExit = 0)
  for image in myimages:
    imagelb.append(image.name,image.id)

  # Allow Flavor Selection
  flavortb = snack.Textbox(13,1,"Flavor: ",scroll=0,wrap=0) 
  flavorlb = snack.Listbox(height = 3, width = 50, returnExit = 0)
  for flavor in myflavors:
    flavorlb.append(flavor.name,flavor.id)

  
  bb = snack.ButtonBar(newsrvwin, (("Ok", "ok"), ("Quit", "quit")))

  g = snack.GridForm(newsrvwin, title, 2, 10)

  # name entry row
  g.add(nametb, 0, 0)
  g.add(namee, 1, 0)

  # image entry row
  g.add(imagetb, 0, 1, padding=(0,1,0,1))
  g.add(imagelb, 1, 1, padding=(0,1,0,1))

  # flavor entry row
  g.add(flavortb, 0, 2, padding=(0,1,0,1))
  g.add(flavorlb, 1, 2, padding=(0,1,0,1))

  g.add(bb, 0, 3, growx = 1)

  result = g.runOnce()


  newsrvwin.finish()

  if bb.buttonPressed(result) == "ok":
    return namee
  else:
    return  bb.buttonPressed(result)


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

    # Add a new server to the active datacenter 
    if mcsrun == "server_add":
      createServerForm(help_text, "New Cloud Server for %s" % curregion, myservers, myimages, myflavors, mykeypairs, mynetworks) 
    # Return to the main menu with the results of cred actions
    if mcsrun == 'quit':
      return 

