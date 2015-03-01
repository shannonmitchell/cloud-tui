#!/usr/bin/python

# Import external modules 
import time
import snack
import pyrax
import keyring



#######################################################
# Snack form to get server info from a user
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

  # Select any public keys attache to the server's root
  keypairtb = snack.Textbox(13,1,"Keypair: ",scroll=0,wrap=0) 
  keypairlb = snack.Listbox(height = 3, width = 50, returnExit = 0)
  for keypair in mykeypairs:
    keypairlb.append(keypair.name, keypair.name)

  # Select networks to attach to the server
  networktb = snack.Textbox(13,1,"Networks: ",scroll=0,wrap=0) 
  networkcbt = snack.CheckboxTree(height = 3, scroll = 0)
  for network in mynetworks:
    if network.name == 'private' or network.name == 'public':
      networkcbt.append(network.name, network, selected = 1)
    else:
      networkcbt.append(network.name, network, selected = 0)
  

  
  bb = snack.ButtonBar(newsrvwin, (("Add", "add"), ("Cancel", "cancel")))

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

  # keypair entry row
  g.add(keypairtb, 0, 3, padding=(0,1,0,1))
  g.add(keypairlb, 1, 3, padding=(0,1,0,1))

  # network entry row
  g.add(networktb, 0, 4, padding=(0,1,0,1))
  g.add(networkcbt, 1, 4, padding=(0,1,0,1))

  g.add(bb, 0, 5, growx = 1)

  result = g.runOnce()

  newsrvwin.finish()

  if bb.buttonPressed(result) == "add":
    # Create a dict to return
    retval = {
      'servername': namee.value(),
      'imageid': imagelb.current(), 
      'flavorid': flavorlb.current(), 
      'keypairname': keypairlb.current(),
      'networklist': networkcbt.getSelection(),
    }
    return retval
  else:
    return  bb.buttonPressed(result)


##########################################################
# Select then delete a server
##########################################################
def deleteServer(helpline, title, servers, srvobj):

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
    # Ask if they really want to delete this one.
    deleteid = li.current()
    delobj =  0
    for server in servers:
      if server.id == deleteid:
        delobj = server
    mainlswin = snack.SnackScreen()
    mainlswin.pushHelpLine(helpline)
    question = snack.ButtonChoiceWindow(mainlswin, 
                            "Are you Sure?", 
                            "%s: %s" % (delobj.name, delobj.id), 
                            buttons = ['Delete', 'No!!! Keep it'], 
                            width = 60, x = None, y = None, help = None)
    mainlswin.finish()

    # if the delete button was pushed do the needful
    if 'delete' in question:

      # Make a quick display to show the user we are
      # updating the server list
      infowin = snack.SnackScreen()
      infowin.pushHelpLine(helpline)
      tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)
      g = snack.GridForm(infowin, "Waiting for server to delete", 1, 10)
      g.add(tb, 0, 0)
      g.draw()

      # Put real delete after the draw to reduce flash
      delobj.delete()

      while True:
        text = "\nRefreshing Server Objects..."
        tb.setText(text)
        infowin.refresh()
        myservers = srvobj.list()
        found = 0
        for server in myservers:
          if server.id == delobj.id:
            found = 1
            text += "\nServer still exists..."
            tb.setText(text)
            infowin.refresh()

        if found == 1:
          text += "\nSleeping 20 seconds..."
          tb.setText(text)
          infowin.refresh()
          time.sleep(20)
        else:
          break
          
      infowin.finish()

  else:
    return  bb.buttonPressed(result)


##########################################################
# Display all of the servers and return the selected
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
# Add a New Server and Display Results
#########################################
def addServer(help_text, title, srvobj, svals):

  # Start the informational gui
  infowin = snack.SnackScreen()

  # Set the help line
  infowin.pushHelpLine(help_text)

  # Create an object to throw the text in
  tb = snack.Textbox(80, 20, "", scroll = 0, wrap = 1)

  g = snack.GridForm(infowin, title, 1, 2)
  bb = snack.Button("Continue")
  g.add(tb, 0, 0)
  g.add(bb, 0, 1)
  g.draw()

  text = "Adding Server..."
  tb.setText(text)
  infowin.refresh()

  net_list = []
  for network in svals['networklist']:
    net_list.append({'net-id': network.id})

  server = srvobj.servers.create(svals['servername'], 
                                 svals['imageid'],
                                 svals['flavorid'],
                                 key_name=svals['keypairname'],
                                 nics=net_list 
                                 )

  text += "\nServer ID: %s" % server.id
  text += "\nAdmin Pass: %s" % server.adminPass
  text += "\nServer Status: %s" % server.status
  text += "\nNetworks: %s" % server.networks
  tb.setText(text)
  infowin.refresh()

  text += "\nWaiting on build to complete..."
  text += "\nGet some coffee.  This could take a while..."
  tb.setText(text)
  infowin.refresh()

  new_srv = pyrax.utils.wait_until(server, "status", ["ACTIVE", "ERROR"])
  text += "\nBuild Complete:"
  text += "\n  Server ID: %s" % new_srv.id
  text += "\n  Admin Pass: %s" % server.adminPass
  text += "\n  Server Status: %s" % new_srv.status
  text += "\n  Networks: %s" % new_srv.networks
  tb.setText(text)
  infowin.refresh()

  # Add a continue button
  g.runOnce()

  infowin.finish()





#########################################
# Display the primary server screen
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

  ###################################################
  # Throw up a information window while loading data
  ###################################################

  # Start the informational gui
  infowin = snack.SnackScreen()

  # Set the help line
  infowin.pushHelpLine(help_text)

  # Create an object to throw the text in
  tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)

  g = snack.GridForm(infowin, "Loading Server Data", 1, 10)
  g.add(tb, 0, 0)
  g.draw()

  # Set up pyrax to prepare for server actions
  text = "Setting up Cloud Session..."
  tb.setText(text)
  infowin.refresh()
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
  text +=  "\nPulling Server Objects..."
  tb.setText(text)
  infowin.refresh()
  myservers = srvobj.list()

  text += "\nPulling Image Objects..."
  tb.setText(text)
  infowin.refresh()
  myimages = srvobj.images.list()

  text += "\nPulling Flavor Objects..."
  tb.setText(text)
  infowin.refresh()
  myflavors = srvobj.flavors.list()

  text += "\nPulling Keypairs..."
  tb.setText(text)
  infowin.refresh()
  mykeypairs = srvobj.keypairs.list()

  text += "\nPulling Networks..."
  tb.setText(text)
  infowin.refresh()
  mynetworks = netobj.list()

  infowin.finish()



  ###################################
  # Run the main server screen loop
  ###################################
  while True:

    # Print the main servers screen
    ################################
    mcsrun = mainServersScreen(help_text)


    # Simple list the servers for the active datacenter 
    if mcsrun == "server_list":
      listServers(help_text, "Server List for %s" % curregion, myservers)

    # Delete a selected server.  This will take two actions.  
    if mcsrun == "server_del":
      retval = deleteServer(help_text, "Delete a server in %s" % curregion, myservers, srvobj)

      if retval != "quit":
        # Make a quick display to show the user we are
        # updating the server list
        infowin = snack.SnackScreen()
        infowin.pushHelpLine(help_text)
        tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)
        g = snack.GridForm(infowin, "Loading Server Data", 1, 10)
        g.add(tb, 0, 0)
        g.draw()
        text = "\nRefreshing Server Objects..."
        tb.setText(text)
        infowin.refresh()
        myservers = srvobj.list()
        infowin.finish()

    # Add a new server to the active datacenter 
    if mcsrun == "server_add":
      formvals = createServerForm(help_text, "New Cloud Server for %s" % curregion, myservers, myimages, myflavors, mykeypairs, mynetworks) 

      if formvals != 'cancel':
        addServer(help_text, "Adding New Cloud Server %s" % formvals['servername'], srvobj, formvals) 

        # Make a quick display to show the user we are
        # updating the server list
        infowin = snack.SnackScreen()
        infowin.pushHelpLine(help_text)
        tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)
        g = snack.GridForm(infowin, "Loading Server Data", 1, 10)
        g.add(tb, 0, 0)
        g.draw()
        text = "\nRefreshing Server Objects..."
        tb.setText(text)
        infowin.refresh()
        myservers = srvobj.list()
        infowin.finish()





    # Return to the main menu with the results of server actions
    if mcsrun == 'quit':
      return 

