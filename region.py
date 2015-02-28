#!/usr/bin/python

# Import external modules 
import snack


#########################################
# Display the primary credentials screen
#########################################
def regionSelectScreen(help_text, selected_creds, curregion):


  # Set up the main screen 
  regwin = snack.SnackScreen()

  # Set the help line
  regwin.pushHelpLine(help_text)
  
  regions = ["DFW", "IAD", "ORD", "LON", "SYD"]
  li = snack.Listbox(height = 10, width = 40, returnExit = 0)
  for region in regions:
      li.append(region, region)

  li.setCurrent(curregion)

  bb = snack.ButtonBar(regwin, (("o(k)", "ok", 'k'), ("(q)uit", "quit", 'q')))

  g = snack.GridForm(regwin, "Select Region", 1, 4)
  g.add(li, 0, 0)
  g.add(bb, 0, 3, growx = 1)


  result = g.runOnce()

  regwin.finish()

  if bb.buttonPressed(result) == "ok":
    return li.current()
  else:
    return  bb.buttonPressed(result)


