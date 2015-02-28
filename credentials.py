#!/usr/bin/python

# Import external modules 
import snack
import pyrax
import keyring


################################################
# Edit entries in the Python keyring
################################################
def editKeyRingEntries(curvals, newvals):

  i = 0
  while(True):
    description = keyring.get_password("cloud-tui", "%s_desc" % i)
    # Edit if it exists(don't want two entries with the same name)
    if curvals[0] == description:
      try:
        keyring.set_password("cloud-tui", "%s_desc" % i, newvals[0])
        keyring.set_password("cloud-tui", "%s_tenant" % i, newvals[1])
        keyring.set_password("cloud-tui", "%s_user" % i, newvals[2])
        keyring.set_password("cloud-tui", "%s_apikey" % i, newvals[3])
        #print "stored keyring for service cloud-tui and key %s_desc" % i
      except keyring.errors.PasswordSetError:
        print "Could NOT edit keyring for service cloud-tui and key %s_desc" % i
      break
    
    i += 1

  

################################################
# Use Python keyring to add cloud credentials
################################################
def addKeyRingEntries(curvals):

  i = 0
  while(True):
    description = keyring.get_password("cloud-tui", "%s_desc" % i)
    # Edit if it exists(don't want two entries with the same name)
    if curvals[0] == description:
      break
    
    # Break if at end of the list, else increment and move on
    if description == None:
      break
    else:
      i += 1

  try:
    keyring.set_password("cloud-tui", "%s_desc" % i, curvals[0])
    keyring.set_password("cloud-tui", "%s_tenant" % i, curvals[1])
    keyring.set_password("cloud-tui", "%s_user" % i, curvals[2])
    keyring.set_password("cloud-tui", "%s_apikey" % i, curvals[3])
    #print "stored keyring for service cloud-tui and key %s_desc" % i
  except keyring.errors.PasswordSetError:
    print "Could NOT store keyring for service cloud-tui and key %s_desc" % i
  


#######################################################
# Delete the given entry
#######################################################
def deleteKeyRingEntries(curvals):


  # Get the last entry id
  last = 0
  while(True):
    description = keyring.get_password("cloud-tui", "%s_desc" % last)
    if description == None:
      break
    else:
      last += 1

  # Delete if the last entry, otherwise disable it.
  # The keyring doens't make it easy to rename objects.
  i = 0
  while(True):
    description = keyring.get_password("cloud-tui", "%s_desc" % i)

    # Delete if it exists
    if curvals[0] == description:
    
      try:
        if i == last:
          keyring.delete_password("cloud-tui", "%s_desc" % i)
        else:
          keyring.set_password("cloud-tui", "%s_desc" % i, "deleted")
        keyring.delete_password("cloud-tui", "%s_tenant" % i)
        keyring.delete_password("cloud-tui", "%s_user" % i)
        keyring.delete_password("cloud-tui", "%s_apikey" % i)
        #print "deleted entry %s_desc" % i
      except keyring.errors.PasswordSetError:
        print "Could NOT delete entry %s_desc" % i
      break

    i += 1



#######################################################
# Get all available keyring entries for all cloud-tui
#######################################################
def getKeyRingEntries():

  # Init the return var
  returnvar = []

  # Run through until you find all of the entries
  # 1_tenant, 1_user, 1_apikey, 1_desc
  i = 0
  while(True):
    description = keyring.get_password("cloud-tui", "%s_desc" % i)
    if description == None:
      break
    else:
      curkey = "%s_desc" % i
      cur_desc = description
      cur_user = keyring.get_password("cloud-tui", "%s_user" % i)
      cur_tenant = keyring.get_password("cloud-tui", "%s_tenant" % i)
      cur_apikey = keyring.get_password("cloud-tui", "%s_apikey" % i)
      # Don't append "deleted" entries
      if 'deleted' not in cur_desc:
        returnvar.append((cur_desc,cur_tenant,cur_user,cur_apikey))
      i += 1

  return returnvar





#######################################################
# Snack form to get credential info from a user
#######################################################
def createCredentialsForm(helpline, title, inptext):

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


#######################################################
# Snack form to edit credential info from a user
#######################################################
def editCredentialsForm(helpline, title, inptext, curcreds):

  # Set up the main screen 
  credwin = snack.SnackScreen()

  # Set the help line
  credwin.pushHelpLine(helpline)
  
  # Get user entries
  ew = snack.EntryWindow(credwin, title, inptext,
                         [
                           ('Description:', curcreds[0]),
                           ('Tenant:', curcreds[1]),
                           ('Username:', curcreds[2]),
                           ('API Key:', curcreds[3]),
                         ],
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
def selectCredential(helpline, title):

  # get the current key ring entries
  krentries = getKeyRingEntries()

  # Set up the main screen 
  mainscrwin = snack.SnackScreen()

  # Set the help line
  mainscrwin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 40, returnExit = 0)
  for krentry in krentries:
    li.append(krentry[0],krentry)

  bb = snack.ButtonBar(mainscrwin, (("(o)k", "ok", 'o'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(mainscrwin, title, 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  mainscrwin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)



#########################################
# Display the primary credentials screen
#########################################
def mainCredentialsScreen(helpline):


  # Set up the main screen 
  maincrwin = snack.SnackScreen()

  # Set the help line
  maincrwin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 40, returnExit = 0)
  li.append("s - Select Active Credential", "credential_select")
  li.append("a - Add Credential", "credential_add")
  li.append("d - Delete Credential", "credential_delete")
  li.append("e - Edit Credential", "credential_edit")

  bb = snack.ButtonBar(maincrwin, (("(o)k", "ok", 'o'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(maincrwin, "Manage Keystore Entries", 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  maincrwin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)



#######################################
# Main loop for the credentials menus  
#######################################
def mainCredentialsScreenLoop(help_text, selected_creds, curregion):


  # call mainScreen
  while True:

    # Print the main cred screen
    ################################
    mcsrun = mainCredentialsScreen(help_text)


    # Select Credential
    ###################
    if mcsrun == 'credential_select':
      curselected_creds = selectCredential(help_text, "Select Active Credential")

      if curselected_creds != "quit":
        selected_cred = curselected_creds
        help_text = "(%s) %s" % (curregion, selected_creds[0])



    # Delete Credential
    ###################
    if mcsrun == 'credential_delete':
      help_text = "(%s) %s" % (curregion, selected_creds[0])
      del_creds = selectCredential(help_text, "Select Credential to Delete")

      # Not a good idea to delete the active credential
      while del_creds[0] == selected_creds[0] and del_creds != "quit":
        help_text = "(%s) %s  !!!! Can't delete the active cred !!!!" % (
                                                                curregion,
                                                                curregiondel_creds[0])
        del_creds = selectCredential(help_text, "Select Credential to Delete")

      # Delete the current selected cred
      if del_creds != "quit":
        deleteKeyRingEntries(del_creds)
      


    # Add Credential
    ################
    if mcsrun == 'credential_add':
      # get the user input
      formvals = createCredentialsForm(help_text, 
                                        "Add Credential",
                                        "Input Cloud Credential Information")


      if formvals != "quit":

        # add it to the keyring
        addKeyRingEntries(formvals)

        # convert the array to a tuple used for the rest of the application
        created_creds = (formvals[0], formvals[1], formvals[2], formvals[3])  

        # set the selected_creds so that the newly created one will be the
        # active one on menu exit.
        selected_creds = created_creds
        help_text = "(%s) %s" % (curregion, created_creds[0])


    # Edit Credential 
    ##################
    if mcsrun == 'credential_edit':
 
      # Select one to edit
      help_text = "(%s) %s" % (curregion, selected_creds[0])
      old_creds = selectCredential(help_text, "Select Credential to Edit")

      # get the user input
      formvals = editCredentialsForm(help_text, 
                                        "Edit Credential",
                                        "Edit Cloud Credential Information",
                                        old_creds)


      if formvals != "quit":


        # convert the array to a tuple used for the rest of the application
        edited_creds = (formvals[0], formvals[1], formvals[2], formvals[3])  

        # add it to the keyring
        editKeyRingEntries(old_creds, edited_creds)

        # Set the active if thats the one edited 
        if old_creds[0] == selected_creds[0]:
          selected_creds = edited_creds
          help_text = "(%s) %s" % (curregion, edited_creds[0])


    # Return to the main menu with the results of cred actions
    if mcsrun == 'quit':
      return selected_creds 

