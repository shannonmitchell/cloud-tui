#!/usr/bin/python -W ignore

# Import external modules
import os
import sys
import time
import pyrax
import snack
import region
import keyring
import servers
import networks
import warnings
import credentials 

# The '-W ignore' in the pytho args gets rid of the novaclient 1.1 warning

# Disable the ssl cert warning
from requests.packages.urllib3 import exceptions
warnings.simplefilter("ignore", exceptions.SecurityWarning)



def mainScreen(helpline):

  # Set up the main screen 
  mainwin = snack.SnackScreen()

  # Set the help line
  mainwin.pushHelpLine(helpline)
  

  li = snack.Listbox(height = 10, width = 40, returnExit = 0)
  li.append("s - Cloud Servers", "cloud_servers")
  li.append("n - Cloud Networks", "cloud_networks")
  li.append("l - Cloud Load Balancers", "cloud_load_balancer")
  li.append("c - Manage Credentials", "credentials") 
  li.append("r - Change Default Region", "change_active_region") 

  bb = snack.ButtonBar(mainwin, (("(o)k", "ok", 'o'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(mainwin, "Rackspace Cloud TUI", 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  mainwin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)

  



def main():

  # Set the default region to work out of
  default_region = "DFW"


  # Set the default help text. Ended up using an array to put diffent notifications
  help_text = " "

  # keep track of the returned active cred tuple
  active_cred_tup = ()

  # If you have no credentials in the keystore, create the default
  # If you do then set the first entry with an index of 0 to default
  keyentries = credentials.getKeyRingEntries()
  if keyentries == []:
    formvals = credentials.createCredentialsForm(" ", 
                                        "Add Credential",
                                        "You must create your initial credentials first")

    credentials.addKeyRingEntries(formvals) 
    active_cred_tup = (formvals[0], formvals[1], formvals[2], formvals[3])
  else:
    # Set the default as the active cred
    active_cred_tup = keyentries[0]
    help_text = "(%s) %s" % (default_region, active_cred_tup[0])
    



  # call mainScreen
  while True:

    # Print the main screen
    msrun = mainScreen(help_text)

    if msrun == 'credentials':

      # Jump to the main credentials submenu
      credtup = credentials.mainCredentialsScreenLoop(help_text, active_cred_tup, default_region)

      # update the active_cred_tup and set the help text
      active_cred_tup = credtup
      help_text = "(%s) %s" % (default_region, active_cred_tup[0])

    if msrun == 'change_active_region':
    
      # Jump to the region select screen
      newregion = region.regionSelectScreen(help_text, active_cred_tup, default_region)
      if newregion != "quit":
        default_region = newregion
        help_text = "(%s) %s" % (default_region, active_cred_tup[0])


    if msrun == 'cloud_servers':
      servers.mainServersScreenLoop(help_text, active_cred_tup, default_region)



    if msrun == 'cloud_networks':
      networks.mainNetworksScreenLoop(help_text, active_cred_tup, default_region)



    if msrun == 'quit':
      sys.exit()


  



if __name__ == '__main__':
  main()

