"this is a test" 


import os
import shutil

def SetupSymb():
    """This function creates local copies of symbology. """
    destsymbdir = "C:\Mapping_Project\MXDs\Symbology"
    if not os.path.exists("C:\Mapping_Project\MXDs\Symbology"):
        os.mkdir("C:\Mapping_Project\MXDs\Symbology")
    if not os.path.exists("C:\Mapping_Project\MXDs\Symbology\PercentChange.lyr"):
        for fl in glob(r"\\ca1ntap01\grm\PAT\ArcMappingTool\Symbology\PercentChange\\*"):
            shutil.copy2(fl,destsymbdir)
def SetupPerilsEUWS(maptype):
    """ Moves the RMS MXD template and shapefiles from the GRM drive to the local drive. MXD location is hardcoded. Maptype options = 'CRESTA' or 'POST'"""
    destmxddir = "C:\Mapping_Project\MXDs"
    destSHPdir = "C:\Mapping_Project\Shapefiles"

    SetupSymb()
    if maptype == 'CRESTA':
        try:
            shutil.copy2(r"\\ca1ntap01\grm\PAT\ArcMappingTool\MXDs\EUWS\EUWS_CRESTA.mxd",destmxddir)
        except:
            if os.path.exists("C:\Mapping_Project\MXDs\EUWS_CRESTA.mxd") :
                    print "The EUWS map already exists on your local machine."
            else:
                print "Error with SetupPerilsEUWS"

        for fl in glob(r"\\ca1ntap01\grm\PAT\ArcMappingTool\Shapefiles\EUWS_CRESTA\*"):
            try:
                shutil.copy2(fl,destSHPdir)
            except:
                print "Was not able to copy over ", os.path.basename(fl)
    if maptype == 'POST':
        try:
            shutil.copy2(r"\\ca1ntap01\grm\PAT\ArcMappingTool\MXDs\EUWS\EUWS_Postcode.mxd",destmxddir)
        except:
            if os.path.exists("C:\Mapping_Project\MXDs\EUWS_Postcode.mxd") :
                    print "The EUWS map already exists on your local machine."
            else:
                print "Error with SetupPerilsEUWS"

        for fl in glob(r"\\ca1ntap01\grm\PAT\ArcMappingTool\Shapefiles\EUWS_Postcode\*"):
            try:
                shutil.copy2(fl,destSHPdir)
            except:
                print "Was not able to copy over ", os.path.basename(fl)

def SetupPerilsEUFL(maptype):
    """ Moves the RMS MXD template and shapefiles from the GRM drive to the local drive. MXD location is hardcoded. Maptype options = 'CRESTA' or 'POST'"""
    destmxddir = "C:\Mapping_Project\MXDs"
    destSHPdir = "C:\Mapping_Project\Shapefiles"

    SetupSymb()
    if maptype == 'CRESTA':
        try:
            shutil.copy2(r"\\ca1ntap01\grm\PAT\ArcMappingTool\MXDs\EUFL\EUFL_CRESTA.mxd",destmxddir)
        except:
            if os.path.exists("C:\Mapping_Project\MXDs\EUFL_CRESTA.mxd") :
                    print "The EUFL map already exists on your local machine."
            else:
                print "Error with SetupPerilsEUFL"

        for fl in glob(r"\\ca1ntap01\grm\PAT\ArcMappingTool\Shapefiles\EUFL_CRESTA\*"):
            try:
                shutil.copy2(fl,destSHPdir)
            except:
                print "Was not able to copy over ", os.path.basename(fl)
    if maptype == 'POST':
        try:
            shutil.copy2(r"\\ca1ntap01\grm\PAT\ArcMappingTool\MXDs\EUFL\EUFL_Postcode.mxd",destmxddir)
        except:
            if os.path.exists("C:\Mapping_Project\MXDs\EUFL_Postcode.mxd") :
                    print "The EUFL map already exists on your local machine."
            else:
                print "Error with SetupPerilsEUFL"

        for fl in glob(r"\\ca1ntap01\grm\PAT\ArcMappingTool\Shapefiles\EUFL_Postcode\*"):
            try:
                shutil.copy2(fl,destSHPdir)
            except:
                print "Was not able to copy over ", os.path.basename(fl)

