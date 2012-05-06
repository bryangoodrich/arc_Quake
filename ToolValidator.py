class ToolValidator:
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    import arcpy
    self.params = arcpy.GetParameterInfo()


  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    self.params[3].enabled = False  # Overwrite Flag unavailable until
                                    # currently existing file selected    
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    if (self.params[0].value and self.params[1].altered and self.params[1].value):
      import os.path
      outfile = os.path.join(str(self.params[0].value), self.params[1].value)
      if arcpy.Exists(outfile):
        self.params[3].enabled = True
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    return
