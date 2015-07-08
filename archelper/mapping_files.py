"""
This module helps reduce the need to know arcpy for mapping. There are a few basic functions here that, when combined correctly, can create any number of maps quickly. This tool can use multiple CSVs, columns, and MXDs to create a large number of maps. Module users should use the create_dir() function first to set-up the correct C:/Mapping_Project structure. This module is designed to work with a csv containing values that should be mapped using graduated symbology. The user needs a CSV, shapefiles for mapping, mapping documents (.mxd files), and symbology.




"""

import os
import operator
import arcpy
from glob import glob

def create_dir():
    """Creates an empty folder directory on the C drive called Mapping_Project. """
    try:
        if not os.path.exists("C:/Mapping_Project"):
            os.mkdir("C:/Mapping_Project")

        if not os.path.exists("C:/Mapping_Project/MXDs"):
            os.mkdir("C:/Mapping_Project/MXDs")

        if not os.path.exists("C:/Mapping_Project/Shapefiles"):
            os.mkdir("C:/Mapping_Project/Shapefiles")

        if not os.path.exists("C:/Mapping_Project/Out"):
            os.mkdir("C:/Mapping_Project/Out")
    except:
        print "There was an error creating the directories."

def create_workspace():
    """Checks if a .gbp workspace exists. If there is not one, the script will make one. This script returns the path of the workspace. The .gbp workspace is useful for working with csv data.
    """
    path = 'C://Mapping_Project//workspace.gdb'
    if not os.path.exists('C://Mapping_Project//workspace.gdb'):
        arcpy.CreateFileGDB_management('C://Mapping_Project//', 'workspace.gdb')
    else:
        print 'you already have a workspace there'
    return  path



def csv_checkmissingshpvals(csvfile,joincol, shpfile, shpfileheader):
    """This script will check to see if any join column values in the CSV are missing in the shapefile. Returns a list of missing shapefile join data.CheckMissingSHPVals(csvfile should be a filepath. joincol is the column index in the csv starting at 0. shapefile is shapefile path. shapefile header should be the column lookup name.)"""
    csvvals = []
    with open(csvfile) as csv:
        csv.next()
        for L in csv:
            csvvals.append(l.split(',')[joincol])
    shpvals = []
    rows = arcpy.SearchCursor(shpfile,fields = shpfileheader)
    for row in rows:
        shpvals.append(str(row.getValue(shpfileheader)))
    results = []
    for val in csvvals:
        if val not in shpvals:
            results.append(val)
    if results == []:
        print "All values were joined"
    return results

def csv_getcols(csvfile):
    """ Returns a list of the CSV headers."""
    with open(csvfile, 'rb') as csv:
        cols = csv.next().strip().split(',')
    return cols

def csv_getall(csvfile):
    """ Prints the lines in an unformatted csv. To join the csv, please use the JoinCSV function.
    """
    with open(csvfile) as csv:
        for L in csv:
            print l

def csv_sort(csvfile, colindex = 0, reverse = False):
    """ This script will sort a csv based on the colindex and csvfile path. If reverse is True, the values will be sorted in reverse index. This function assumes that the csv has headers. colindex starts at 0.
    """
    data = []
    with open(csvfile,'r') as f:
        for line in f:
            data.append(line)
    header = csv.reader(data, delimiter=",").next()
    reader = csv.reader(data[1:], delimiter=",")
    if reverse:
        sortedlist = sorted(reader, key=operator.itemgetter(colindex),reverse = True)
    else:
        sortedlist = sorted(reader, key=operator.itemgetter(colindex))
    os.remove(csvfile)
    ResultFile = open(csvfile,'wb')
    wr = csv.writer(ResultFile)
    wr.writerow(header)
    for L in sortedlist:
        wr.writerow(l)
    ResultFile.close()
    print "Finished sorting the csv"

def csv_jointable(csvfile, workspace):
    """ This function will import the csv to the workspace. This datatable will then be imported to a shapefile using the JoinSHP() function. This returns a string of the workspace and table name"""
    tablename = os.path.basename(csvfile).rstrip('.csv')
    try:
        arcpy.Delete_management(workspace + '//' + tablename)
        arcpy.TableToTable_conversion(csvfile, workspace, tablename)
        print "Old table in workspace deleted, replaced by new table ", workspace + '//'+tablename
    except:
        arcpy.TableToTable_conversion(csvfile, workspace, tablename)
        print "New table in workspace added to the workspace with name ", workspace + '//'+tablename
    return workspace + '//'+tablename


def shp_getcols(shapefile):
    """Returns a list of shapefile columns."""
    mylist = []
    for field in arcpy.ListFields(shapefile):
        mylist.append(str(field.name.strip()))

    return mylist

def shp_removecols(shapefile, cols):
    """Removes fields from shapefile specified in the cols list. Columns can only have 10 characters."""
    for col in cols:
        col = col[:10]
        if arcpy.ListFields(shapefile, col):
            arcpy.DeleteField_management(shapefile, col)
            print 'Field deleted:', col
        else:
            print 'No field to delete:', col

def shp_addcols(shapefile, cols, datatype):
    """ Adds each column in the list of cols. Columns can only have 10 characters. All columns added will be given the same datatype.

        Possible fields types:

        TEXT Any string of characters.
        FLOAT  Fractional numbers between -3.4E38 and 1.2E38.
        DOUBLE  Fractional numbers between -2.2E308 and 1.8E308.
        SHORT  Whole numbers between -32,768 and 32,767.
        LONG  Whole numbers between -2,147,483,648 and 2,147,483,647.
        DATE Date and/or time.
        BLOB Long sequence of binary numbers. You need a custom loader or viewer or a third-party application to load items into a BLOB field or view the contents of a BLOB field.
        RASTER Raster images. All ArcGIS software-supported raster dataset formats can be stored, but it is highly recommended that only small images be used.
        GUID Globally unique identifier.

        If you try to add a duplicate column that is already in the shapefile, the existing duplicate column will be deleted.
    """
    if type(cols) is list:
        for col in cols:
            col = col[:10]
            if arcpy.ListFields(shapefile, col):
                print 'Removed existing column from the shapefile:', col
                arcpy.DeleteField_management(shapefile, col)
                arcpy.AddField_management(shapefile, col, datatype)
            else:
                arcpy.AddField_management(shapefile, col, datatype)
            print 'Added column to the shapefile:', col, datatype
    else:
        col = cols[:10]
        if arcpy.ListFields(shapefile, col):
            print 'Removed existing column from the shapefile:', col
            arcpy.DeleteField_management(shapefile, col)
            arcpy.AddField_management(shapefile, col, datatype)
        else:
            arcpy.AddField_management(shapefile, col, datatype)
        print 'Added column to the shapefile:', col, datatype

def shp_joincsv(csvfile, shapefile, shapefilejoincol, csvjoinindex, csvfieldindex):
    """ This function manually joins the CSV to the shapefile and does not use geodatabase tables like the JoinCSV() and JoinSHP() functions. This method should be easier and faster in most cases. In the CSV, the join column must be before the columns with mapping values. This code will map all fields from the mapping column onward (to the right). Returns missing cols. Column limit should be 10 characters."""

    cols = GetCSVcols(csvfile)

    i = 0
    newcols = []
    for col in cols:
        if i >= csvfieldindex:
            newcols.append(col[:10])
        i += 1

    AddSHPcols(shapefile, newcols, "double")
    i = 0
    ct = 0
    csvjoinlist = []

    with open(csvfile, 'rb') as csvfile:
        lib = dict()
        csvfile.next() #scip the headers
        for L in csvfile:
            line = l.rstrip().split(",")
            csvjoinlist.append(line[csvjoinindex])
            lib[line[csvjoinindex]] = lib.get(line[csvjoinindex],line[csvfieldindex:])

    rows = arcpy.UpdateCursor(shapefile)
    #rows = arcpy.UpdateCursor(shpfile,"","","","%s %s" % (shapefilejoincol, method)) ##sorted
    shpjoinlist = []
    missingshpvals = []
    for row in rows:
        shpjoinval = str(row.getValue(shapefilejoincol))
        shpjoinlist.append(shpjoinval)
        try:
            vals = lib.get(shpjoinval)
            for ind, field in enumerate(newcols):
                row.setValue(str(field),float(vals[ind]))
                rows.updateRow(row)
        except:
            pass
            # missingshpvals.append(shpjoinval) #This is the shapefile value that there is no corresponding CSV value for. This list is for debugging.
    # missingcsvvals = []
    # for L in csvjoinlist:
    #     if L not in shpjoinlist:
    #         missingcsvvals.append(l)

    return #missingcsvvals #these values are missing



def shp_jointable(jointable, joinfield, shapefile, shpjoinfield, add_fields):
    """ Joins the workspace table to the shapefile. The workspace table is generated by csv_jointable().  jointable and shapefile should be the full path of the file ie. C:/path/to/shapefile.shp and c:path/to/workspace.gbp/tablename """
    new_fields = []
    for col in add_fields:
        col = col[:10]
        new_fields.append(col)
        if arcpy.ListFields(shapefile, col):
            arcpy.DeleteField_management(shapefile, col)
    arcpy.JoinField_management(shapefile, shpjoinfield,jointable, joinfield, new_fields)
    print "Finished shapefile join."







def CalcPerChangeSHP(shapefile, shapejoincol, aggregation_column, maxmin_cols):
    """This function will loop through a shapefile and group values based upon the specified 'aggregation_column'. The function will then calculate the maximum and minimum for each of the maxmin_cols specified. A new field will be added to the shapefile that included "L_" and the first 8 characters of each value in the maxmin_cols. Use these new columns to label the max and min values when creating maps. Returns the new label columns"""
    newcols = []
    for col in maxmin_cols:
        newcols.append("L_" + col[:8])
    AddSHPcols(shapefile, newcols, "STRING")

    rows = arcpy.SearchCursor(shapefile)
    shpvallist = []
    joinlist = []
    for row in rows:
        vals = {}
        vals[aggregation_column] = str(row.getValue(aggregation_column))
        vals[shapejoincol] = str(row.getValue(shapejoincol))
        joinlist.append(vals[aggregation_column])
        for val in maxmin_cols:
            vals[val[:10]] = float(row.getValue(val[:10]))
        shpvallist.append(vals)
    # print shpvallist[:10]
    joinlist = set(joinlist)
    coldict = {}
    for col in maxmin_cols:
        col = col[:10]
        newdict = {}
        for adminval in joinlist:
            vals = []
            for row in shpvallist:
                if row[aggregation_column] == adminval:
                    postalcode = row[shapejoincol]
                    if int(row[col]) == -9999: #use -9999 as a key for no data
                        val = ''
                    else:
                        val = row[col]
                    vals.append((postalcode, val))
            # try:
            i = 0
            for postalcode, val in vals:
                if val == -9999:
                    continue
                elif i == 0:
                    maxpost, maxval = postalcode, val
                    minpost, minval = postalcode, val
                elif val > maxval:
                    maxpost, maxval = postalcode, val
                elif val < minval:
                    minpost, minval = postalcode, val
                i += 1
            i = 0
            newdict[adminval] = (maxpost, maxval,minpost, minval)
        coldict[col] = newdict

    for col in maxmin_cols:
        col = col[:10]
        l_col = "L_" + str(col)[:8]
        vals = coldict[col]
        del rows
        rows = arcpy.UpdateCursor(shapefile)
        for row in rows:
            shpjoinval = row.getValue(aggregation_column)
            post = row.getValue(shapejoincol)
            currentval = row.getValue(col)
            maxpost = vals[shpjoinval][0]
            minpost = vals[shpjoinval][2]
            if post in (maxpost, minpost):
                row.setValue(l_col,"{0:.0f}%".format(currentval*100))
                rows.updateRow(row)
    print "Finished adding the max and min percent change values to the shapefile. Here are the new column headers"
    print newcols
    return newcols

def CalculateField(shapefile, fieldname, py_expression):
    """Calculate values for a field given a python expression as a string. The py expression should be formatted with ! characters before and after the field name. ie.py_expression ='str(!POSTCODE!) + '_' + str(!JOIN!) """
    arcpy.CalculateField_management (shapefile, fieldname, py_expression,"Python")


def GetMXDList():
    return glob(os.path.join("C:/Mapping_Project/MXDs","*.mxd"))

def GetLayers(mxds):
    """Prints the available layers in the mxd document. A string version of the layer name is returned. GetLayers(mxds = 'mxdpath' or ['mxdpath1','mxdpath2'])"""

    lyrlist = []
    if type(mxds) is list:
        for mxdpath in mxds:
            print mxdpath
            mxd = arcpy.mapping.MapDocument(mxdpath)
            i = 0
            for lyr in arcpy.mapping.ListLayers(mxd):
                lyrlist.append([os.path.basename(mxdpath), str(lyr.name), i])
                i += 1
        print 'MXD/tLAYER/tLAYER_INDEX'
        for row in lyrlist:
            print row
        return lyrlist
    elif type(mxds) is str:
        mxd = arcpy.mapping.MapDocument(mxds)
        i = 0
        for lyr in arcpy.mapping.ListLayers(mxd):
            lyrlist.append([os.path.basename(mxds), str(lyr.name), i])
            i += 1
        print 'MXD/tLAYER/tLAYER_INDEX'
        for row in lyrlist:
            print row
        return lyrlist
    else:
        print "The mxd needs to be formatted as a list, not a string. add brackets around the variable ['mxdpath']"

def CreateMaps(mxds,shapefile, mapfields,symbology, labels = False):
    """This function will create maps for all mxds specified and all fields in the mapfields list. The symbology options = 'Percent_Change' and 'Diff_LC'. If the symbology does not exist locally, this function will copy the necessary files from the network into the mxd/symbology folder. """
    i= 0
    for col in mapfields:
        mapfields[i] = col[:10]
        i += 1
    i = 0
    if type(mxds) is str:
        newmxd = []
        newmxd.append(mxds)
        mxds = newmxd
    if type(mapfields) is str:
        newmapfields = []
        newmapfields.append(mapfields)
        mapfields = newmapfields

    mapresolution = 300 #300 is common.

    if symbology.lower() == "percent_change":
        symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
    elif symbology.lower() == "diff_lc":
        symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
    elif symbology [-4:] == '.lyr':
        symbpath = arcpy.mapping.Layer(symbology)
    else:
        print "You need to choose a symbology type: 'Percent_Change','Diff_LC', or a layerpath"
        return
    for mxd in mxds:
        mxdobj = arcpy.mapping.MapDocument(mxd)
        df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)
        for lyr in arcpy.mapping.ListLayers(mxdobj):
            if lyr.name == os.path.basename(shapefile).replace(".shp",""): #leave as default for these maps(will it change for other perils????)
                lyr.symbologyType == "GRADUATED_COLORS"

                for field in mapfields:
                    arcpy.mapping.UpdateLayer(df, lyr, symbpath, True) #if you get a value error, it could be because of the layers source symbology no longer being available. It could also be because of a join issue or incorrect column names. The column name character limit is 10.
                    lyr.symbology.valueField = field
                    if labels:
                            lyr.showLabels = True
                            if symbology.lower() == "percent_change":
                                expres = "str(int(round(float(["+field[:10]+"])*100,0))) + '%'"
                            elif symbology.lower() == "diff_lc":
                                expres = "str(round(float(["+field[:10]+"]),3))"
                            for lblClass in lyr.labelClasses:
                                lblClass.expression = expres
                                lblClass.SQLQuery = field +" <> -9999"
                                lblClass.showClassLabels = True
                    else:
                        lyr.showLabels = False
                    arcpy.RefreshActiveView()
                    arcpy.mapping.ExportToJPEG(mxdobj, "C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + field +".jpg", resolution=mapresolution)
                    print "New map: C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + ".jpg"

def CreateMaps2(mxds,shp1, shp2,  mapfields,symbology, labels1 = False,labels2 = False):
    """This function will create maps for all mxds specified and all fields in the mapfields list. The symbology options = 'Percent_Change' and 'Diff_LC'. This function will update the symbology and labels for two shapefiles. They must have the same mapfields. Symbology options are diff_lc and percent_change. If labels1 or labels2 is True, the mapfields will be labelled """

    i= 0
    for col in mapfields:
        mapfields[i] = col[:10]
        i += 1

    if type(mxds) is str:
        newmxd = []
        newmxd.append(mxds)
        mxds = newmxd
    if type(mapfields) is str:
        newmapfields = []
        newmapfields.append(mapfields)
        mapfields = newmapfields

    mapresolution = 300 #300 is common.

    if symbology.lower() == "percent_change":
        symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
    elif symbology.lower() == "diff_lc":
        symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
    else:
        print "You need to choose a symbology type: 'Percent_Change' or 'Diff_LC'"
        return
    for mxd in mxds:
        mxdobj = arcpy.mapping.MapDocument(mxd)
        df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)

        for lyr in arcpy.mapping.ListLayers(mxdobj):
            if lyr.name == os.path.basename(shp1).replace(".shp",""):
                lyr1 = lyr
            elif lyr.name == os.path.basename(shp2).replace(".shp",""):
                lyr2 = lyr

        lyr1.symbologyType == "GRADUATED_COLORS"
        lyr2.symbologyType == "GRADUATED_COLORS"

        for field in mapfields:
            field = field [:10]
            print os.path.basename(mxd).rstrip(".mxd"), field
            arcpy.mapping.UpdateLayer(df, lyr1, symbpath, True)
            if symbology.lower() == "percent_change":
                expres = "str(int(round(float(["+field+"])*100,0))) + '%'"
            elif symbology.lower() == "diff_lc":
                expres = "str(int(round(float(["+field+"])*100,0)))"
            lyr1.symbology.valueField = field
            if labels1:
                if lyr1.supports("LABELCLASSES"):
                    lyr1.showLabels = True
                # print "Layer name: " + lyr1.name
                    for lblClass in lyr1.labelClasses:
                        lblClass.expression = expres
                        lblClass.SQLQuery = field +" <> -9999"
                        lblClass.showClassLabels = True
            else:
                lyr1.showLabels = False

            arcpy.mapping.UpdateLayer(df, lyr2, symbpath, True)
            lyr2.symbology.valueField = field

            if labels2:
                if lyr2.supports("LABELCLASSES"):
                    lyr2.showLabels = True
                # print "Layer name: " + lyr2.name
                    for lblClass in lyr2.labelClasses:
                        lblClass.expression = expres
                        lblClass.SQLQuery = field +" <> -9999"
                        lblClass.showClassLabels = True
            else:
                lyr2.showLabels = False

            arcpy.RefreshActiveView()
            arcpy.mapping.ExportToJPEG(mxdobj, "C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + symbology +".jpg", resolution=mapresolution)
            print "New map: C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + symbology +".jpg"


def CreateMaps3(mxds,shapefile,mapfields, labelfields, symbology):
    """This function will create maps for all mxds specified and all fields in the mapfields list. The symbology options = 'Percent_Change' and 'Diff_LC'. This function allows specification of different label fields for the mapfields labels. ie use mapfields as difference in loss cost, but label the max and min percent change column. The mapfields and labelfields lists must be ordered in the same order so that the first value of mapfields will get labelled with the first value in labelfields."""

    i= 0
    for col in mapfields:
        mapfields[i] = col[:10]
        i += 1

    if type(mxds) is str:
        newmxd = []
        newmxd.append(mxds)
        mxds = newmxd
    if type(mapfields) is str:
        newmapfields = []
        newmapfields.append(mapfields)
        mapfields = newmapfields

    mapresolution = 300 #300 is common.

    if symbology.lower() == "percent_change":
        symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
    elif symbology.lower() == "diff_lc":
        symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
    else:
        print "You need to choose a symbology type: 'Percent_Change' or 'Diff_LC'"
        return
    for mxd in mxds:
        mxdobj = arcpy.mapping.MapDocument(mxd)
        df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)

        for lyr in arcpy.mapping.ListLayers(mxdobj):
            if lyr.name == os.path.basename(shapefile).replace(".shp",""):
                lyr.symbologyType == "GRADUATED_COLORS"
                for field, label in zip(mapfields, labelfields):
                    field = field [:10]
                    label = label [:10]
                    print field, label

                    arcpy.mapping.UpdateLayer(df, lyr, symbpath, True)
                    lyr.symbology.valueField = field
                    expres = "["+label+"]"
                    print expres
                    if lyr.supports("LABELCLASSES"):
                        lyr.showLabels = True
                        for lblClass in lyr.labelClasses:
                            lblClass.expression = expres
                            lblClass.SQLQuery = field +" <> -9999"
                            lblClass.showClassLabels = True
                    arcpy.RefreshActiveView()
                    arcpy.mapping.ExportToJPEG(mxdobj, "C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + symbology +".jpg", resolution=mapresolution)
                    print "New map: C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + field + symbology +".jpg"




def CreateMaps4(mxds,shapefile,shpsubregioncol, mapfields, labelfields, symbology):
    """This function will create maps for all mxds specified and all fields in the mapfields list. The symbology options = 'Percent_Change' and 'Diff_LC'. This function allows specification of different label fields for the mapfields labels. ie use mapfields as difference in loss cost, but label the max and min percent change column. The mapfields and labelfields lists must be ordered in the same order so that the first value of mapfields will get labelled with the first value in labelfields. This function will zoom to the different layer attributes specified in the shpsubregioncol field."""
    i= 0
    for col in mapfields:
        mapfields[i] = col[:10]
        i += 1
    i = 0
    for col in labelfields:
        labelfields[i] = col[:10]
        i += 1

    if type(mxds) is str:
        newmxd = []
        newmxd.append(mxds)
        mxds = newmxd
    if type(mapfields) is str:
        newmapfields = []
        newmapfields.append(mapfields)
        mapfields = newmapfields
    if type(labelfields) is str:
        newlabelfields = []
        newlabelfields.append(mapfields)
        labelfieldsfields = newlabelfields

    mapresolution = 300 #300 is common.

    if symbology.lower() == "percent_change":
        symbpath = arcpy.mapping.Layer("C:/Mapping_Project/MXDs/Symbology/PercentChange.lyr")
    elif symbology.lower() == "diff_lc":
        symbpath = arcpy.mapping.Layer('C:/Mapping_Project/MXDs/Symbology/DifferenceinLossCost.lyr')
    else:
        print "You need to choose a symbology type: 'Percent_Change' or 'Diff_LC'"
        return


    rows = arcpy.SearchCursor(shapefile)
    adminIDs = []
    for row in rows:
        val = row.getValue(shpsubregioncol)
        if val not in adminIDs:
            adminIDs.append(val)
    del rows

    for mxd in mxds:
        mxdobj = arcpy.mapping.MapDocument(mxd)
        df = arcpy.mapping.ListDataFrames(mxdobj)[0] #leave as default for these maps(will it change for other perils????)


        for lyr in arcpy.mapping.ListLayers(mxdobj):
            if lyr.name == "EUFL_RL15_Zips_Cover":
                lyr2 = lyr
            elif lyr.name == "EUFL_RL15_Zips_Cover2":
                lyr3 = lyr

        for lyr in arcpy.mapping.ListLayers(mxdobj):
            if lyr.name == os.path.basename(shapefile).replace(".shp",""):
                lyr.symbologyType == "GRADUATED_COLORS"
                for field, label in zip(mapfields, labelfields):
                    field = field [:10]
                    label = label [:10]
                    arcpy.mapping.UpdateLayer(df, lyr, symbpath, True)
                    lyr.symbology.valueField = field
                    expres = "str(int(round(float(["+label+"]) *100,0))) + '%'"
                    print expres
                    if lyr.supports("LABELCLASSES"):
                        print "here"
                        lyr.showLabels = True
                        for lblClass in lyr.labelClasses:
                            lblClass.expression = expres
                            lblClass.SQLQuery = field +" <> -9999"
                            lblClass.showClassLabels = True

                    for adminID in adminIDs:
                        if adminID[:2] in ['BE','UK','GM']:
                            adminID = str(adminID)

                            query1 = '"'+ shpsubregioncol + '" = ' + "'" + adminID + "'"
                            query2 = '"'+ shpsubregioncol + '" <> ' + "'" + adminID + "'"
                            query3 = '"'+ shpsubregioncol + '" <> ' + "'" + adminID + "'"
                            print shpsubregioncol, adminID, query1
                            lyr.definitionQuery =  query1
                            lyr2.definitionQuery = query2
                            lyr3.definitionQuery = query3

                            ext = lyr.getSelectedExtent(True)
                            df.extent = ext
                            # df.panToExtent(lyr.getSelectedExtent())
                            # df.zoomToSelectedFeatures()
                            arcpy.RefreshActiveView()
                            arcpy.mapping.ExportToJPEG(mxdobj, "C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + adminID + "_" + field + symbology + ".jpg", resolution=mapresolution)
                            print "New map: C:/Mapping_Project/Out/"+ os.path.basename(mxd).rstrip('.mxd') +'_' + adminID +"_" +field + symbology + ".jpg"


###############################################################################

def JoinSHPspecial(shapefile, shapejoincol, shapefile2, shapejoincol2, addcols):
    """Not using this function for the project, but it works, so i'm leaving it here. This function adds max and min values associated with shapefile1 to shapefile2. If shapefile 1 has 3 postcodes in a county, this script will add the max and min value to shapefile 2 for that county. The value -9999 in a shpfile is treated as unknown rather than a minimum change."""
    i= 0
    for col in addcols:
        addcols[i] = col[:10]
        i += 1
    i = 0
    AddSHPcols(shapefile2, addcols, "STRING")
    rows = arcpy.SearchCursor(shapefile)
    shpvallist = []
    joinlist = []
    for row in rows:
        vals = {}
        vals[shapejoincol2] = row.getValue(shapejoincol2)
        joinlist.append(vals[shapejoincol2])
        for val in addcols:
            vals[val] = float(row.getValue(val))
        shpvallist.append(vals)

    joinlist = set(joinlist)
    coldict = {}
    for col in addcols:
        newdict = {}
        for adminval in joinlist:
            vals = []
            for row in shpvallist:
                if row[shapejoincol2] == adminval:
                    if int(row[col]) == -9999: #use -9999 as a key for no data
                        vals.append('')
                    else:
                        vals.append(row[col])
            try:
                maxval = max(v for v in vals if v <> '')
            except:
                maxval = "None"
            try:
                minval = min(vals)
            except:
                minval = "None"
            maxval = str(int(round(maxval *100,0)))
            minval = str(int(round(minval *100,0)))
            newdict[adminval] = minval + "% to "+ maxval + "%"
        coldict[col] = newdict

    for col in addcols:
        vals = coldict[col]
        del rows
        rows = arcpy.UpdateCursor(shapefile2)
        for row in rows:
            shpjoinval = row.getValue(shapejoincol2)
            try:
                row.setValue(str(col),str(vals[shpjoinval]))
                rows.updateRow(row)
            except:
                pass





