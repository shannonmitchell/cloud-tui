#!/usr/bin/python

# Import external modules 
import time
import snack
import pyrax
import keyring



#######################################################
# Snack form to get new network info from the user
#######################################################
def createNetworkForm(helpline, title): 

  # Set up the main screen 
  newnetwin = snack.SnackScreen()

  # Set the help line
  newnetwin.pushHelpLine(helpline)
  
  # Get user entries
  nametb = snack.Textbox(13,1,"Network Name: ",scroll=0,wrap=0) 
  namee = snack.Entry(50, text="", hidden = 0, password = 0, scroll = 1, returnExit = 0)

  cidrtb = snack.Textbox(13,1,"Network CIDR: ",scroll=0,wrap=0) 
  cidre = snack.Entry(50, text="", hidden = 0, password = 0, scroll = 1, returnExit = 0)

  bb = snack.ButtonBar(newnetwin, (("Add", "add"), ("Cancel", "cancel")))

  g = snack.GridForm(newnetwin, title, 2, 3)

  # name entry row
  g.add(nametb, 0, 0, padding=(0,1,0,1))
  g.add(namee, 1, 0, padding=(0,1,0,1))

  # cidr entry row
  g.add(cidrtb, 0, 1, padding=(0,0,0,1))
  g.add(cidre, 1, 1, padding=(0,0,0,1))

  # button entry row
  g.add(bb, 0, 2, growx = 1)

  result = g.runOnce()

  newnetwin.finish()

  if bb.buttonPressed(result) == "add":
    retval = {
      'networkname': namee.value(),
      'cidr': cidre.value(),
    }
    return retval
  else:
    return  bb.buttonPressed(result)


##########################################################
# Select a network for deletion
##########################################################
def deleteNetwork(helpline, title, networks):

  # Set up the main screen 
  mainlnwin = snack.SnackScreen()

  # Set the help line
  mainlnwin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 80, returnExit = 0)
  for network in networks:
    full = "label=%-10s cidr=%-20s id=%s" % (network.label, network.cidr, network.id)
    li.append(full,network.id)

  bb = snack.ButtonBar(mainlnwin, (("Delete", "delete"), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(mainlnwin, title, 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)

  result = g.runOnce()

  mainlnwin.finish()

  if bb.buttonPressed(result) == "delete":
    return li.current()
  else:
    return  bb.buttonPressed(result)


##########################################################
# Display all of the networks and return the selected
##########################################################
def listNetworks(helpline, title, networks):

  # Set up the main screen 
  mainlnwin = snack.SnackScreen()

  # Set the help line
  mainlnwin.pushHelpLine(helpline)
  
  labelwidth = 10
  cidrwidth = 20
  idwidth = 30

  # Header
  tbh1 = snack.Textbox(labelwidth, 1, "Label", scroll=0, wrap=0)
  tbh2 = snack.Textbox(cidrwidth, 1, "CIDR", scroll=0, wrap=0)
  tbh3 = snack.Textbox(idwidth, 1, "ID", scroll=0, wrap=0)
  tbl1 = snack.Textbox(labelwidth, 1, "------", scroll=0, wrap=0)
  tbl2 = snack.Textbox(cidrwidth, 1, "----", scroll=0, wrap=0)
  tbl3 = snack.Textbox(idwidth, 1, "--", scroll=0, wrap=0)


  # Loop through and create entries for all of the networks
  tb1 = []
  tb2 = []
  tb3 = []
  for network in networks:
    tb1.append(snack.Textbox(labelwidth, 1, network.label , scroll=0, wrap=0))
    if network.cidr:
      tb2.append(snack.Textbox(cidrwidth, 1, network.cidr, scroll=0, wrap=0))
    else:
      tb2.append(snack.Textbox(cidrwidth, 1, "special", scroll=0, wrap=0))
    if network.id:
      tb3.append(snack.Textbox(idwidth, 1, network.id, scroll=0, wrap=0))
    else:
      tb3.append(snack.Textbox(idwidth, 1, "special", scroll=0, wrap=0))
      

    
  bb = snack.Button("Close")

  g = snack.GridForm(mainlnwin, title, 3, len(networks) + 3)
  g.add(tbh1, 0, 0)
  g.add(tbh2, 1, 0)
  g.add(tbh3, 2, 0)
  g.add(tbl1, 0, 1, padding=(0,0,0,1))
  g.add(tbl2, 1, 1, padding=(0,0,0,1))
  g.add(tbl3, 2, 1, padding=(0,0,0,1))
  for i in range(len(networks)):
    g.add(tb1[i], 0, i + 2)
    g.add(tb2[i], 1, i + 2)
    g.add(tb3[i], 2, i + 2)
 
  i += 3 
  g.add(bb, 0, i, growx = 1, padding=(0,2,0,0))


  result = g.runOnce()

  mainlnwin.finish()

  return 





#########################################
# Display the primary network screen
#########################################
def mainNetworksScreen(helpline):


  # Set up the main screen 
  mainnetwin = snack.SnackScreen()

  # Set the help line
  mainnetwin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 40, returnExit = 0)
  li.append("l - Network List & Info", "network_list")
  li.append("a - Add Network", "network_add")
  li.append("d - Delete Network", "network_del")

  bb = snack.ButtonBar(mainnetwin, (("(o)k", "ok", 'o'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(mainnetwin, "Cloud Networks", 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  mainnetwin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)


#######################################
# Main loop for the servers menus  
#######################################
def mainNetworksScreenLoop(help_text, selected_creds, curregion):


  ###################################################
  # Throw up a information window while loading data
  ###################################################

  # Start the informational gui
  infowin = snack.SnackScreen()

  # Set the help line
  infowin.pushHelpLine(help_text)

  # Create an object to throw the text in
  tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)

  g = snack.GridForm(infowin, "Loading Network Data", 1, 10)
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
  netobj = cur_session.get_client("network", curregion)

  # Start pulling some values to assist
  text += "\nPulling Networks..."
  tb.setText(text)
  infowin.refresh()
  mynetworks = netobj.list()
  infowin.finish()



  ###################################
  # Run the main network screen loop
  ###################################
  while True:

    # Print the main servers screen
    ################################
    mcsrun = mainNetworksScreen(help_text)


    # Simple list the servers for the active datacenter 
    if mcsrun == "network_list":

      # Keep looping so the user doesn't get kicked out on a info exit
      lsret = listNetworks(help_text, "Networks List for %s" % curregion, mynetworks)

    # Delete a selected server.  This will take two actions.  
    if mcsrun == "network_del":
      retval = deleteNetwork(help_text, "Delete a network in %s" % curregion, mynetworks)

      if retval != "quit":
        for network in mynetworks:
          if network.id == retval:

            # Make a quick display to show the user we are
            # updating the server list
            infowin = snack.SnackScreen()
            infowin.pushHelpLine(help_text)
            tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)
            g = snack.GridForm(infowin, "Network Delete Progress", 1, 10)
            g.add(tb, 0, 0)
            g.draw()

            text = "\nDeleting Network Object..."
            tb.setText(text)
            infowin.refresh()
            network.delete()

            text += "\nRefreshing Network Objects..."
            tb.setText(text)
            infowin.refresh()

            mynetworks = netobj.list()
            infowin.finish()

    # Add a new server to the active datacenter 
    if mcsrun == "network_add":
      formvals = createNetworkForm(help_text, "New Cloud Network for %s" % curregion) 

      if formvals != 'cancel':


        # Make a quick display to show the user we are
        # updating the server list
        infowin = snack.SnackScreen()
        infowin.pushHelpLine(help_text)
        tb = snack.Textbox(40, 10, "", scroll = 0, wrap = 0)
        g = snack.GridForm(infowin, "Network Add Progress", 1, 10)
        g.add(tb, 0, 0)
        g.draw()

        text = "\nAdding New Network Object..."
        tb.setText(text)
        infowin.refresh()
        netobj.create(formvals['networkname'], cidr=formvals['cidr'])

        text += "\nRefreshing Network Objects..."
        tb.setText(text)
        infowin.refresh()

        mynetworks = netobj.list()
        infowin.finish()





    # Return to the main menu with the results of server actions
    if mcsrun == 'quit':
      return 

