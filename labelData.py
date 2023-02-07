# Author Nigel Slack
# Date 11/Mar/2022

# Held in Github : https://github.com/NigelSlack/Axivity-Sensor/blob/main/labelData.py

import subprocess
import sys
import os

configFile = "sensorcodeConfigFile.txt"

helpText = """

This code has seven basic functions : 

  1. Label records in csv or xlsx files. The first variable in each record must be a timestamp, and there must be at least one other numeric variable.
     A plot is displayed of the time against selected numeric value(s). The user selects portions of the plot, and assigns a label to each portion. 
     An output file is produced containing the selected columns and time periods, with each record having the appropriate label appended to it. 
     The labels are chosen from a list held in the file sensorcodeConfigFile.txt in the same folder as the code.
     Labels can be added or deleted. If the labels are changed the sensorcodeConfigFile.txt is updated, and the user can also create a copy of the 
     program code containing the new labels. If the config file is deleted, or the code run elsewhere, the new labels will be output to the new config
     file.
     
     Time periods for which the user allocates the label 'Other' are excluded from the output file.  
     If the user selects any 'Other' labels, the timestamps of subsequent periods are adjusted to run immediately consecutive to the period preceding 
     that for 'Other'. The timestamps will no longer be the actual timestamps, but this does not affect using the output files for training models, and
     using the trained models for making predictions.
     
     The user can specify which columns to include in the output file.
     For example, an input file record might contain - 2022/04/15 12.36.10  -0.963  0.72  0.23  54  
       - a timestamp with accelerometer x,y and z values and a heartrate
       If the user just wants the accelerometer data, plus timestamps and labels in the output file, they can select columns 0 to 3, and perhaps add a 
       human activity label to the time period containing this record of 'Walk'. The corresponding record in the output file will then be - 
       2022/04/15 12.36.10  -0.963  0.72  0.23  Walk

     If there are multiple records per second in the input file, the user can select the proportion to keep (with records in the input file randomly 
     selected) for  inclusion in the output file. eg if there are 200 records per second in the input file the user might decide to keep an average of 
     10 per second in the output file.

     Scaling can be applied to numeric values in the input file, either to the data itself, or just for the plot. For example, in the record above if 
     the last value  (heartrate) is included in the plot then the 3 accelorometer values will be squashed together at the bottom of the plot, with a big 
     gap separating them and the heartrate. If the output file is to be used to build predictive models (for future unlabelled data) the user may wish to 
     experiment with using scaled or unscaled data to see which results in the best predictions. 
     The user can opt for both scaled and unscaled outputs - it may be useful for comparing model predictions with scaled/unscaled inputs.
     
     The user can add a 'root mean squared' value to the output file, ie the square root of the sum of the squares of selected variables.
     
     The file type of the output file is set to the same as for the input file, eg if the input file is a csv file, then the output file will also be csv.
     A summary file is also produced, with '-sum' appended to the output data file name, showing the mean and standard deviation of each of the numeric 
     variables, for each distinct period with respect to the labels applied. For example, if the labels 'Walk' and 'Sit' were chosen for the first 15 minutes 
     and the second 15 minutes respectively, then the mean values (and standard deviations) are shown for numeric values over these two periods.
     A subjectid (eg person's name or initials) and a sensor location (eg left wrist or waist) can be included in the summary records.      

  2. Combine csv/xlsx files. The user selects files to combine, and each one is appended to the output file. As for option one, the user can select specific
     columns (variables) to include, can scale values, and can specify a proportion of input records to include in the output file. After the first file has 
     been added to the output file, the the timestamp value for subsequent files is adjusted to follow on from the last record of the previous file, at a second
     or minute level, depending on the gradation present in the first file - if the timestamps in the first file are at second level, timestamps for subsequent 
     files will start at a value one second after the last timestamp of the previous file. If they are at a minute level, one minute will be added to the last
     record to give the timestamp of the first record of the next file.    
     Input files do not need to contain the same number of columns (variables), so, for example, a file containing a timestamp and heartrate variable could be 
     appended to one cotaining a timestamp and 3 accelerometer variables. The file type of the first file determines the type of the output file, eg if the first 
     file specified is an xlsx file, then the output file will be too, although input files do not need to be of the same file type.

  3. Pre-process a file containing (numerical) physiological data. A specific column containing the target data must be selected by the user. The code determines
     the mean of the values in the selected column on a minute by minute basis (M), by blocks of numbers of seconds (S), or by blocks of data containing a specified 
     number of records (B). If the difference in the mean value for a given block of size M/S/B, and the mean value for the block M/S/B preceeding it by two blocks
     of size M/S/B is greater than a specific percentage (chosen by the user), then the values for the block of M/S/B immediately before the current block of M/S/B
     are set to the same as for the current block. 
     The purpose of this is to attempt to improve the accuracy of models built using this data, that predict eg human activity.
     For example, suppose a user wears two sensors, an accelerometer and a heart rate sensor. They switch between activities, eg sitting, walking, running etc and 
     the readings from the sensors are used to try to predict their activity types.
     When changing activity the accelerometer readings will change in a fraction of a second, but the heartrate may take eg about 30 seconds to adjust. A machine 
     learning model is more likely to make accurate predictions if the heartrate transition is presented as more of a step change than a gradual change.  

  4. Merge two files. Data from the records of one file are appended to the records of another file (unlike for 'combine' where the data are appended to the end 
     of the file).
     For example, if the first file contained 2022/04/15 12.36.10  -0.963  0.72  0.23   and the second contained  2022/04/15 12.36.01  67  (from an accelerometer 
     and a heartrate monitor), then the output record could contain   2022/04/15 12.36.10  -0.963  0.72  0.23  67
     The file with the higher frequency is treated as the primary file - the timestamps will be taken from this file, and the selected columns from it will come
     first. If both files have the same frequency then the first file specified is used as the primary file. Where frequencies differ, values from the file with 
     lower frequency are repeated for an appropriate number of records. For example, if the first file contains 10 records per second, and the second has 5 per 
     minute, then the values from one record of the second file will be appended to 120 records of the first file (as the frequency of the first file is 120 times
     that of the second). This is calculated on a minute by minute basis. If the frequency of the second file exceeds that of the first file for a given minute a 
     warning is output, and excess records from the second file are discarded.
     A plot is produced of the primary file, and the user selects the start and end times of the data to process.
     If the timestamps of the two files are synchronised those of the primary file are used as a driver. If they are not synchronised a plot is also displayed of 
     the secondary file and the user selects the start time only for this file. The records from each file are then processed from these two start times on a minute
     by minute basis. Clearly in this case it is important to choose the correct start time for the secondary file to obtain a valid merge of the data.     
     Specific columns, scaling and the proportion of records to keep can be selected by the user for each file, as for other functions.     

   5. Display a histogram of selected data. Required elements of the input file are plotted on one histogram. If input values have different 
      magnitudes, eg if they include heartrate and accelerometer readings, scaling will be required to produce a meaningful plot. The creation 
      of a GaussianNB machine learning model assumes input data have approximately Normal distribution; a histogram plot of the data can be used 
      to determine if this is the case. The user specifies the number of bins to use.      
    
   6, 7 and 8. Create predictive models from labelled data. kMeans, Machine learning and Neural Network models can be created using labelled input data files. 
     The user specifies the column containing the category that the model may be used to predict, and as for other options the user can choose specific columns, 
     scaling and the proportion of records to keep from the input file. An additional file is created along with the model showing the categories used to create
     the model, and a sample data record.
     For Machine Learning, five different models are created. The estimated accuracy of each model is determined using test data, and displayed to the user.
     
   9, 10, 11. Run a predictive kMeans, Machine Learning or Neural network model to generate labels for an input file (using the categories contained in the data
     file from which the model was created). For example, if a model is created using data from a file generated by sensors monitoring human activity, and the 
     activities performed during data collection were 'Walk', 'Run', 'Sit', then it is only appropriate to run this model against input data collected during these
     activities if the purpose is to attempt to predict the label associated with the data. The code will expect the model to have an accompanying file showing the 
     categories used in its creation, and a sample record (as created by options 5, 6 and 7). An output file is produced with the predicted labels appended to each 
     input data record. 
     For example, if  2022/04/15 12.36.10  -0.963  0.72  0.23  67  is the input data record, then  2022/04/15 12.36.10  -0.963  0.72  0.23  67  Walk   might be the
     output record, where 'Walk' is the label predicted by the model.  
     The output file type will be the same as the input file type.     


Requirements : Python, plus required libraries 
               The code will attempt to install any required libraries that are not already installed at runtime. If it fails to do so a message is output and the 
               run terminates. Where a library is required for a specific function it will only be loaded for that function.               

To run :
  python labelData.py
  
Input and output files and folders are selected by the user from a separate Explorer window.  
All input file records are required to have a timestamp as their first variable (in their first column).

If an input file has potentially ambiguous month and day values (if none of the day values in the data exceed '12'), then the user may swap round the month and day
values - this will be required if the plot of the data is clearly wrong, with values strongly clumped together on the time axis when the user would expect them to be 
evenly distributed. The code  takes a random sample of 20 timestamps from the file to determine if this may be the case, and if no values greater than 12 are detected
in the month/day fields it asks the user if they wish to switch the two.

The Axivity AX3 accelerometer :

This code was originally developed for labelling data from this sensor.
This is a wearable sensor that measures acceleration values in 3 orthogonal directions - x, y and z.
Configuration of the sensor is performed using the 'Open Movement' (OM) software package that accompanies it, via a USB or wireless connection to a computer.
Recording of data is started using OM, activities are undertaken by a user, then recording is stopped in OM.
A compressed data file of type 'cwa' is generated by the sensor, with each record containing a timestamp, acceleration readings in the x, y and z directions,
and temperature readings.
The x, y and z directions will depend on the orientation of the sensor during the time it is recording.
OM has a facility for exporting the resultant 'cwa' files to other file types, such as csv files.
 
This code processes exported files (from OM) of type 'raw csv', with datetime format Y-M-D h:m:s.f, and Accelerometer Units Gravity(g). 

The sensor can record between 12.5 and 500 readings per second (Hz), but the OM software warns that it may not process signals correctly if the rate
is set below 50Hz. It is probably best therefore to use this as a minimum frequency value when configuring the sensor. However, this number of readings
may not be required to determine label type, eg 10 or 20 readings per second may be sufficient to distinguish between different activities.

Means of classifying data - most common techniques - KNN, kmeans and sub-clustering. From review paper -
https://www.researchgate.net/publication/341303680_Unsupervised_Human_Activity_Recognition_Using_the_Clustering_Approach_A_Review
"""

#---------------------------------------------------------------------------------------------------------------------------------------------
# Get required libraries. Check each one loads ok. If not, attempt to 'pip install' it. If this fails, tell the user and terminate the run. 
# Only load the libraries required for the selected function.
#---------------------------------------------------------------------------------------------------------------------------------------------
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def loadLibrary(lib,package="none"):
  global allOk
  tried, done = False, False
  while not done:
    try:
      exec(lib)
# Make the libraries available globally  
      globals().update(locals())
      done = True
    except ModuleNotFoundError:
      if package != "none" and tried == False:
        print("Attempting 'pip install' for ",package)
        try:
          install(package)
          tried = True
        except:  
          if allOk:
            print(" ")
            allOk = False
          print(lib," - import failed. pip install ",package," also failed. Please investigate.") 
          done = True
          pass
      else:  
        if allOk:
          print(" ")
          allOk = False
        print(lib,"- import failed. Please pip install and retry") 
        done = True
        pass

def loadLibraries():
  global allOk, firstRun
  
  print("Please wait, loading libraries...")
  allOk = True
  if firstRun:
    loadLibrary("from tkinter import filedialog as fd")
    loadLibrary("from tkinter import Tk")
    loadLibrary("from csv import reader, writer")
    loadLibrary("import csv")
    loadLibrary("import datetime","datetime")
    loadLibrary("import pandas as pd","pandas")
    loadLibrary("import numpy as np","numpy")
    loadLibrary("import matplotlib.ticker","matplotlib")
    loadLibrary("from dateutil.parser import parse","python-dateutil")
    loadLibrary("from datetime import datetime")
    loadLibrary("import re")
    loadLibrary("import xlsxwriter","XlsxWriter")
    loadLibrary("from openpyxl import load_workbook")  
    loadLibrary("from pathvalidate import ValidationError, validate_filename","pathvalidate")
    loadLibrary("from sklearn import preprocessing")
    
# AutoMinorLocator is used to change the number of minor x-axis 'ticks' (and grid lines) in the data plots
# Here we're setting it to 15 minor ticks between each major tick
    class MyLocator(matplotlib.ticker.AutoMinorLocator):
      def __init__(self, n=15):
        super().__init__(n=n)
    matplotlib.ticker.AutoMinorLocator = MyLocator  
    loadLibrary("import matplotlib.pyplot as plt")
    
  if ("CREATE" in purpose) or ("RUN" in purpose): 
    loadLibrary("from scipy import stats","--user scipy")
    loadLibrary("import pickle")
        
  if not ("PRE-PROCESS" in purpose):     
    loadLibrary("from sklearn.preprocessing import RobustScaler","sklearn")
    
  if "CREATE KMEANS" in purpose: 
    loadLibrary("from sklearn.cluster import KMeans")  
    loadLibrary("from sklearn.preprocessing import MinMaxScaler")
    loadLibrary("from itertools import permutations") 
    
  if "CREATE MACHINE" in purpose: 
    loadLibrary("from sklearn.neighbors import KNeighborsClassifier")
    loadLibrary("from sklearn.tree import DecisionTreeClassifier")
    loadLibrary("from sklearn.svm import SVC")
    loadLibrary("from sklearn.svm import LinearSVC")
    loadLibrary("from sklearn.naive_bayes import GaussianNB")
    loadLibrary("from sklearn.ensemble import BaggingClassifier")
    loadLibrary("from sklearn.ensemble import RandomForestClassifier")  
    loadLibrary("from sklearn.metrics import accuracy_score")  
    loadLibrary("from sklearn.model_selection import train_test_split")  
    loadLibrary("from sklearn.model_selection import GridSearchCV")

  if "CREATE NEURAL" in purpose: 
    loadLibrary("import random")
    loadLibrary("from sklearn.preprocessing import OneHotEncoder")
    loadLibrary("import math")
    loadLibrary("from statistics import mean","statistics")
  
  if ("LABEL CSV" in purpose) or ("MERGE" in purpose): 
    loadLibrary("from datetime import timedelta")
    
  if ("LABEL CSV" in purpose): 
    loadLibrary("import shutil")

  if "NEURAL" in purpose: 
# Disable warning messages output from 'Tensorflow', eg if the computer running the code doesn't have any GPUs
# (which Tensorflow can use to improve performance) 
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
    loadLibrary("import tensorflow as tf","tensorflow")
    loadLibrary("import pkg_resources")
    installed = {pkg.key for pkg in pkg_resources.working_set}
    if "h5py" not in installed:
      install("h5py") 
    if "pyyaml" not in installed:
      install("pyyaml") 

# If a library didn't load, stop.  
  if not allOk:
    print("\nTerminating .. ")
    exit()
  
#-----------------------------------------------------------------------------------------------------------------------------------
# Set up 3 lists - 
#  1. The functions the code performs 
#  2. The labels that can be appended to data
#  3. The location where a sensor is worn
#
# If 'purposeList' changes the code will need changing in the main processing, at the bottom of the code, where an 'if' command is 
# used to determine the processing required. 
# eg this 'if' contains 'elif "Create Neural" in purpose:', so if the text here is changed the 'if' command will need changing too.
#
# The contents of the other two lists don't affect the running of the code, but the actual text in 'labelList' is written into the 
# summary file when labelling data manually, and if models are used for making predictions, the same labels will be applied.
#
# A config file, sensorcodeConfigFile.txt, in the same folder as the source code, is created if it doesn't yet exist, and the contents of
# these three variables are loaded into it. If this config file already exists these variables are loaded from the file, rather than taking
# the values held in the code. The user can change the label list. If they do, the config file is updated, and the user can have a copy of the 
# source code written, with 'labelList' containing the new values. The format of these variables must be maintained for this to work, as well 
# as their order in the code (the first occurence of labelList and locationList (followed by an equals sign) are used to locate the part of
# the code to update. The new copied file is called the same as the source code, with '_copyx' appended to it, where 'x' is an integer >= 1
# ('x' is incremented until a filename is found that is not in use).  
#-----------------------------------------------------------------------------------------------------------------------------------

purposeList =  """
               Purpose - Label csv/xlsx file
               Purpose - Combine csv/xlsx files
               Purpose - Pre-process file with physiological data
               Purpose - Merge two files
               Purpose - Show Histogram
               Purpose - Create kMeans model from labelled file
               Purpose - Create Machine Learning models from labelled file
               Purpose - Create Neural Network model from labelled file               
               Purpose - Run kMeans model against unlabelled file
               Purpose - Run Machine Learning model against unlabelled file
               Purpose - Run Neural Network model against unlabelled file
               Purpose - Help
               Purpose - Exit
               """ 

labelList =    """
               Label - Walk Up/down stairs
               Label - Walk on level
               Label - Drive
               Label - Light house activity
               Label - Heavy house activity
               Label - Run on level
               Label - Sit
               Label - Clap
               Label - Jump
               Label - Other
               """ 

locationList = """
               Location - Left Wrist (LW)
               Location - Right Wrist (RW)
               Location - Left Ankle (LA)
               Location - Right Ankle (RA)
               Location - Waist (WA)
               """ 

#-------------------------------------
# Set up all the remaining functions |
#-------------------------------------

#--------------------------------------------------------------------------------------------------------------------------
# Update 'sensorcodeConfigFile.txt' if the user has amended the list of labels. Create it if it does not currently exist. | 
#--------------------------------------------------------------------------------------------------------------------------
def writeConfigFile(func):
  if func == "User update":
    print("Updating config file ",configFile)
  else:
    print("Creating new config file ",configFile," using 'purposeList', 'labelList' and 'locationList' from the source code.")
  with open(configFile, "w") as text_file:
    text_file.write(purposeList)
    text_file.write(labelList)
    text_file.write(locationList)

#-----------------------------------------------
# Get the contents of sensorcodeConfigFile.txt |
#-----------------------------------------------
def readConfigFile():
  global configData
  with open(configFile, "r") as text_file:
    configData = []
    print("Extracting config information from ",configFile)
    lines = text_file.read().split("\n")    
    for line in lines:
      lineNew = line.strip()
      if len(lineNew) > 0:
        configData.append(lineNew.split(" ",1)[0])  
        configData.append(lineNew.split("-",1)[1].strip())  
  
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Create sensorcodeConfigFile.txt if it does not exist. If it does, read it and check it contains the expected categories. if it doesn't, delete it and recreate it. |  
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getConfigs(func):
  global configData
  print(" ")
  if not os.path.isfile(configFile):
    writeConfigFile(func)
  if func == "User update":
    return

  readConfigFile()
        
  if (not "Purpose" in configData) or (not "Label" in configData) or (not "Location" in configData):
    os.remove(configFile)   
    writeConfigFile("")
    readConfigFile()

#-------------------------------------
# Check if a value is floating point |
#-------------------------------------
def isFloat(element):
  try:
    float(element)
    return True
  except ValueError:
    return False

#---------------------------------
# Check if a value is an integer |
#---------------------------------
def isInt(element):
  try:
    int(element)
    return True
  except ValueError:
    return False

#---------------------------------
# Check if a value is a datetime |
#---------------------------------
def isDatetime(inString):   
  try: 
    parse(str(inString), fuzzy=False)
    return True
  except ValueError:
    return False

#------------------------------------------------------------------
# Ask the user if they wish to continue processing. If not, stop. |  
#------------------------------------------------------------------
def checkIfContinue():
  print(" ")
  if not getYNInput("Continue (Y/N)? - "):
    print("\nTerminating")
    exit()        

#-----------------------------------------------------------------------------------------------------------
# Create a list of options (label/sensor location) to present to the user, with each option being numbered | 
#-----------------------------------------------------------------------------------------------------------
def setupList(paramType):
  global configData
  option = []
  for ix in range(len(configData)):
    if configData[ix].upper() == paramType.upper():
      option.append(configData[ix+1])
  return(option)

#--------------------------------------------------------------------------------------
# Get the user to select an option (created in 'setupList') by specifying it's number |
#--------------------------------------------------------------------------------------
def letUserPick(options):
  global optNum
  done = False
  while not done:
    for idx, element in enumerate(options):
      print("{}) {}".format(idx+1,element))
    i = input("\nEnter number: ")
    try:
      if 0 < int(i) <= len(options):
        done = True
        print(" ")
        optNum = int(i)-1
        return options[int(i)-1]
    except:
      pass

#------------------------------------------------------------------------------------------------------------------------------------
# For each 10 minute or 30 second interval set the label to the most common one currently found within that interval.
# A prediction from eg a Machine Learning algorithm might for example predict a quarter second of clapping surrounded by
# 5 seconds of walking upstairs before and after the clapping. In such a case it is likely the clapping has been mis-characterised. 
# We assume activities are performed for at least 30 seconds, and labelling in 30 second blocks helps eliminate single, or small
# numbers of records being labelled with probable incorrect values - the most common label is most likely to be correct 
# within an interval.
#------------------------------------------------------------------------------------------------------------------------------------
def smoothActivities(predictedAct):
  global perMinute
  ilen = len(predictedAct)
  i = 0
# 'freq' contains the number of data records per second/minute 
  if perMinute:
    numrecs = freq * 10
    print("Frequency smoothed")
  else:  
    numrecs = freq * 30
  ys = []
  while i < ilen:
    labels = predictedAct[i: i + numrecs]
    i+=numrecs
    if i >= ilen:
      numrecs = ilen-(i-numrecs)
    ys.append(numrecs*[stats.mode(labels)[0][0]])
# stats.mode returns the most common value (of predicted labels) in the array
  activities=[x for sublist in ys for x in sublist]  
  return activities

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Switch the values currently held in the month and day positions within a date. The code expects dates to be ordered as yyyy mm dd rather than yyyy dd mm,   |
# and will format dates this way if it is certain which format they are in.                                                                                   |
# If the dates within an input file do not contain day values greater than '12' then we can't be sure which way round they are. Allow the user to swap them   |
# if necessary. A random sample of 20 records is taken, and checked for values greater than '12' in the positions that may be month/day. If the month and day |
# are the wrong way round, plots of the data will look incorrect - clumped together on the x-axis (datetime), rather than spread out evenly.                  |
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def procSwitchMonthDay():
  global df, smd, askUser
  
# If a value greater than '12' is detected, then we know which format we have, so don't need to switch here.
  dfRand = df.sample(n = 20)
  for index, row in dfRand.iterrows():
    rowTime = row[0].strftime(dForm)
    if (int(rowTime[5:7]) > 12) or (int(rowTime[8:10]) > 12):
      return 

# Ask the user if they want to switch month/day - they may have tried running without switching, and found the plot looked incorrect. 
  if askUser:
    print("\nExample record :")
    print(df.iloc[1])
    if not getYNInput("\nSwitch month and day positions in datetime (Y/N)? - "):
      smd = False
      return
  else:
    if not smd:
      return    

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Switch the month/day values by converting the timestamp to a string, switching them in the string, then converting back to a timestamp.                            |
# Somehow (it is not known how by the author) the conversion back to a timestamp can adjust the values passed in the string according to daylight saving differences |
# (or possibly timezone). If this happens, adjust the timestamp by multiples of 30 minutes until it reflects the time in the string.                                 |
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
  smd = True      
  dTime, newCol = "", []
  print("\nPlease wait, converting timestamps ...")
  for index, row in df.iterrows():
    row = row.values.tolist()
    if dTime != row[0]:
      dTime = row[0]
      dTimex = str(dTime)
      d2 = dTimex[0:5] + dTimex[8:10] + dTimex[4:7] + dTimex[10:] 
      element = datetime.strptime(d2,dForm)
      timestamp = datetime.timestamp(element)   
      newstamp = pd.to_datetime(timestamp,unit='s')  
      while str(newstamp) < d2:
        newstamp = newstamp + pd.Timedelta(minutes=30)     
      while str(newstamp) > d2:
        newstamp = newstamp - pd.Timedelta(minutes=30)     
    newCol.append(newstamp)
  df['Time'] = newCol  

#------------------------------------------------------------------------------------------------------------------
# Get a list of column numbers from the user - to determine which columns are processed/passed to an output file. |  
#------------------------------------------------------------------------------------------------------------------
def getColumnNumbers():
  global colNums, numCols, df, includeCol, targetCol
  if numCols > 2:
    colNums = selectColumns(df.iloc[0],"Select the columns to process by column number (first column is column 0. CR for all columns). eg 2,3,4 or 2-4,6,7-9 - ",1)
# Insert the Timestamp column if it wasn't specified - this must always be present
    if colNums[0] != 0:
      colNums.insert(0,0)
# If the user has already selected a 'category' column for creating a model, make sure this is included if it was missed out when the user
# selected column numbers      
    if includeCol not in colNums:
      colNums.append(includeCol) 
      colNums = sorted(colNums)
# If a category column number was specified by the user before, it's column number may have changed if the user didn't select all columns
# to be included in the output file. Find what it's column number is now.      
    if includeCol > 0:  
      targetCol = colNums.index(includeCol)
  else: 
    colNums = [0,1]
    
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Timestamps read from an input file may be given down to 'second' level, but data is actually held at a 'minute' level (with the 'second' value always being '00'). |
# For some of the data processing we need to know if we are looking for changes in the 'second' or 'minute' value from one data record to the next.                  |
# If the datetime changes from one record to the next, but the 'second' value is '00' in both, then the data must be held at 'minute' level.                         | 
# The flag 'perMinute' is set to indicate this.                                                                                                                      |
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
def checkPerMinuteSub(row):
  global firstRec, fPeriod, nextRec, newPeriod, secondPart, breakVar, perMinute, checked
  row = row.values.tolist()
  rowTime = row[0]
  if firstRec:
    firstRec = False
    fPeriod = rowTime
  if rowTime != fPeriod:          
    if nextRec:
      newPeriod = rowTime
      secondPart = str(rowTime)[-2:]
      nextRec = False
    else:
      if newPeriod != rowTime:
        checked = True
        secondPart2 = str(rowTime)[-2:]
        if secondPart == "00" and secondPart2 == "00":
          breakVar, perMinute = True, True
        else:  
          breakVar, perMinute = True, False

#------------------------------------------------------------------------
# Check if data in an input file is held at 'second' or 'minute' level. |
#------------------------------------------------------------------------
def checkPerMinute(df):
  global perMinute, dForm, breakVar, firstRec, nextRec, checked
  if not "%S" in dForm:
    return True 

  firstRec, nextRec, breakVar, checked = True, True, False, False 
  for index, row in df.iterrows():
    checkPerMinuteSub(row)
    if breakVar:
      break

  if not checked:
    print("\nInvalid file selected")
    print("Terminating")
    exit()

  return perMinute

#-----------------------------------------------------------------------------------------------
# Find the per second/minute frequency within data by checking for a change in the time value. | 
#-----------------------------------------------------------------------------------------------   
def getFrequency():
  global df, freq
  fPeriod = df.iloc[0,0]
  freq = 0
  for index, row in df.iterrows():
    rowTime = row[0]
    if rowTime != fPeriod:       
      if freq == 0:
        newPeriod = rowTime
      else:
        if newPeriod != rowTime:
          break
      freq+=1

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Extract the data from a file into a csv/excel (Pandas) dataframe. Remove any rows with empty values.                                                                                |
# Check the first part of each record in a random sample is a timestamp, and that there is at least one numeric value within each record (as a basic input file format verification). |
# If a predictive model is being created ask the user for the column containing the 'category' (the label that the model is to be used to predict), and check the number of           |
# categories in the column. There must be at least 2. If there are more than 10 ask the user if they have selected the correct column, otherwise display the categories.              |
# Make sure the first column is in datetime format, then determine what the format is. If the datetime is at 'microsecond' level convert it to 'second' level.                        |
# Check if records are actually held at 'minute' level but using a 'second' level timestamp (with '00' for the 'second').                                                             |
# Check if month and day values may need to be switched.                                                                                                                              |
# Ask the user which columns they wish to process - to be manipulated/included in an output file/model.                                                                               |
# Find the per second/minute frequency of the data records.                                                                                                                           |
# Ask the user if they wish to scale the data - the actual data values, or just for plotting (or neither).                                                                            |
# If data is held at a 'second' rather than 'minute' level, ask the user how many records they wish to keep per second.                                                               |
# Adjust the dataframe according to each response from the user.                                                                                                                      |
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getData(filename):
  global df, perMinute, dForm, askCols, csvFile, freq, headers, headers2, dFormOrig, scalePlot, numCols, half, numericCols, tPeriod
  global includeCol, combineFile, perSec, si, purpose, targetCol, uniqueLabel, dFrac, dfNoScale, twoOutputs
  print("\nPlease wait, loading file ...") 

# Get file contents
  if csvFile:
    df = pd.read_csv(filename)   
  else:
    df = pd.read_excel(filename)  

  df.dropna(axis=0, how='any', inplace=True)

  headers = [f'Col {i}' for i in range(1,len(df.iloc[0]))] 
  headers.insert(0,"Time")
  df.columns = headers

# Perform basic data verification checks
  numSamp = min(5,len(df)) 
  if numSamp == 0:
    file_stats = os.stat(filename)
    if file_stats.st_size == 0:
      print("\nInvalid file selected. It is empty.")
    else:
      print("\nInvalid file selected")
    print("Terminating")
    exit()

# Carry out basic data checks
  if "CREATE" in purpose.upper():
    minCols = 3
  else:
    minCols = 2  
  dfRand = df.sample(n = numSamp)

  for index, row in dfRand.iterrows():
    if not isDatetime(row[0]):
      print("\nInvalid file selected. Each record must have a datetime as the first element.")
      print("Terminating")
      exit()
    if len(row) < minCols:  
      if minCols == 3:
        print("\nInvalid file selected. Each record must have a datetime as the first element, at least one numeric element, and a category.")
      else:
        print("\nInvalid file selected. Each record must have a datetime as the first element, and at least one numeric element.")
      print("Terminating")
      exit()
    numericCol = False
    for i in range(1,len(row)):
      if (isInt(df.iloc[0][i]) or isFloat(df.iloc[0][i])):
        numericCol = True
    if not numericCol:
      print("\nInvalid file selected. Each record must have a datetime as the first element, and at least one numeric element.")
      print("Terminating")
      exit()

# Get the category - value to be predicted - if creating a model
  numCols = len(df.iloc[0])
  includeCol = 0
  if "CREATE" in purpose.upper():
    targetCol = selectSingleColumn('\nEnter the number of the column containing the categories for the model (CR for last column; first column is column 0) : ',False)    
    numUnique = df.iloc[:,targetCol].nunique()
    if (numUnique < 2):
      print("\nAt least two categories are required in the category column of the input file for creating predictive models.")
      print("Please select a different input file. Terminating.")
      exit()
    elif (numUnique > 10):
      print("There are ",numUnique," categories in the selected column.")
      if not getYNInput("Continue (Y/N) - "):
        print("Terminating.")
        exit()        
    else:
      print("\nCategories contained in the selected column - ")
      print(df.iloc[:,targetCol].unique())
    uniqueLabel = list(df.iloc[:,targetCol].unique())
    includeCol = targetCol

# Make sure the first element is in datetime format  
  headers = [f'Col {i}' for i in range(1,numCols)] 
  headers.insert(0,"Time")
  df.columns = headers
  df['Time'] = pd.to_datetime(df['Time'])

# Convert microsecond timestamps to 'second'  
  dForm = findDateTimeFormat(df.iloc[0,0])
  if "%f" in dForm:
    df['Time'] = df['Time'].dt.round('1s') 
    dForm = "%Y/%m/%d %H:%M:%S"

# See if data is held at 'minute' level but with datetimes at 'second' level
  perMinute = checkPerMinute(df)

# 'tperiod' is used for incrementing timestamps in some processing
  if "%S" in dForm:
    tPeriod = {'quantity': '1', 'time': 'seconds'}
  else:
    tPeriod = {'quantity': '1', 'time': 'minutes'}
  tPeriod = {tPeriod['time']: int(tPeriod['quantity'])} 

# See if month/day should be switched
  procSwitchMonthDay()    

# Ask which columns (elements in each input record) to process
  getColumnNumbers()   
  df = df.iloc[:,colNums].copy()
  
  numCols = len(df.iloc[0])
  headers = [f'Col {i}' for i in range(1,numCols)] 
  headers.insert(0,"Time")
  df.columns = headers
  headers2 = headers
  headers2.append("label")
  
# Make sure datetimes are in a known format
  dFormOrig = dForm
  startTime = setDatetimeFormat(df.iloc[0,0],dForm)
 
# Find the per second/minute frequency
  getFrequency() 
  
# Find which columns contain numeric data  
  numericCols = []
  for i in range(1,numCols):
    if (isInt(df.iloc[0][i]) or isFloat(df.iloc[0][i])):
      df[df.columns[i]] = df[df.columns[i]].astype(float)
      numericCols.append(i)

# Ask if data should be scaled.
  scalePlot = scaleInputData() 

# If data is held at a 'second' level, ask the user how many records to keep/process per second. If the user requested scaled and unscaled outputs, create subsets of the data for both.    
  if ("%S" in dForm) and not perMinute and freq > 5:
    if askUser:
      print("\nInput data has ",freq," readings per second")
      perSec = getPerSec(freq)
      dFrac = round(perSec/freq,2)
    df = df.sample(frac=dFrac).sort_index()
    if twoOutputs:
      dfNoScale = dfNoScale.sample(frac=dFrac).sort_index()
    freq = perSec
  else:  
    dFrac = 1
    
  half = int(freq/2)+1  
    
#---------------------------------------------------------------------------------------------------------------------------------
# Ask the user to select a folder. A separate Explorer window opens (in 'askdirectory') from which the user can select a folder. |
#---------------------------------------------------------------------------------------------------------------------------------
def selectFolder(defaultFolder,txt):
  response = ""
  folder = defaultFolder
  while response != "D" and response != "S":
    response = input(txt).upper()   
    if response == "S":
      root = Tk(); root.withdraw()
      folder = fd.askdirectory()
      root.destroy()
  print("\nSelected folder - ",folder)
  return folder
  
#----------------------------------------  
# Insert a title on a (matplotlib) plot |
#----------------------------------------  
def tellme(s):
    plt.title(s, fontsize=12)
    plt.draw()

#--------------------------------------------
# Get a Yes(Y)/No(N) response from the user | 
#--------------------------------------------   
def getYNInput(txt):  
  yn = ""
  while yn != "Y" and yn != "N":
    yn = input(txt).upper()
  if yn == "Y":  
    return True
  else:
    return False  
  
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Scale data so that large values for one variable don't have an undue influence on an algorithm, resulting in the values of other variables being under-represented |
# in processing, or so that a plot does not have one or more variables separated from each other by large gaps, making it difficult to determine the changes in      |
# one or more variables from the plot. Ask if the user wants both scaled and un-scaled outputs.                                                                      |
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------   
def scaleInputData():
  global df, dfScaledPlot, scaleCols, scaleColumns, headers, scalePlot, numericCols, si, askUser, dfNoScale, purpose, twoOutputs
  twoOutputs = False
  if askUser:
    scalePlot, si = False, ""
    if ("LABEL CSV" in purpose): 
      while si != "N" and si != "P" and si != "D" and si != "B":
        si = input("\nScale input data? No(N), For Plot Only(P), For Plot and Data(D), For Plot and Data plus create un-scaled data too (B) - ").upper()
    else:
      while si != "N" and si != "P" and si != "D":
        si = input("\nScale input data? No(N), For Plot Only(P), For Plot and Data(D)  - ").upper()
  if si == "N":  
    return scalePlot

  if si == "B":  
    twoOutputs = True

  done = False 
  while not done:  
    done = True
    if len(numericCols) == 1:
      scaleCols = numericCols
    else:  
      scaleCols = selectColumns(df.iloc[0],"Select the columns to scale by column number (first column is column 0. CR for all columns). eg 2,3,4 or 2-4,6,7-9 - ",1)
    for s in scaleCols:
      if s not in numericCols:
        print("Only numeric columns can be scaled")
        done = False
        break
  print("\nScaling data ...")  
  scaleColumns = [headers[i] for i in scaleCols] 
  scaler = RobustScaler()
  scaler = scaler.fit(df[scaleColumns])
  if si == "P":  
    scalePlot = True
    dfScaledPlot = pd.DataFrame(scaler.transform(df[scaleColumns].to_numpy()))
    dfScaledPlot.insert(0,"Time",df["Time"])
  else:
    if twoOutputs:  
      dfNoScale = df.copy()  
    df.loc[:, scaleColumns] = scaler.transform(df[scaleColumns].to_numpy())
    for i in scaleCols:
      df.iloc[:,i] = df.iloc[:,i].round(2)

  return scalePlot

#--------------------------------------------------------------------------------------------------------------------------------------
# When a model is saved, the list of unique categories in the data file used to build the model are saved into a file called          |
# 'activities.csv'. When this model is run to categorize unlabelled data the user is told which categories were contained in the      |
# data the model was trained on. It would be inappropriate to run a model against an unlabelled data file created by a user           |
# for categories for which the model has not been trained. Ask the user if they wish to continue when they have seen the categories.  |
# For a Neural Network model the 'activities' file also contains two records showing the length of the blocks that the data was       |
# grouped into, and how much overlap there was between adjacent blocks (in the first 2 records - blockSize and overlap respectively). |
#--------------------------------------------------------------------------------------------------------------------------------------
def showModelActivities(actFile):
  aList, blockSize, overlap = [] , 0 , 0
  with open(actFile, newline='') as f:
    reader = csv.reader(f)
    data = list(reader)  
  f.close()
    
  for d in data:
    if len(d) > 0:
      if str(d[0]).upper() == 'BLOCKSIZE':
        blockSize = d[1]
      if str(d[0]).upper() == 'OVERLAP':
        overlap = d[1]
      if str(d[0]).upper() == 'CATEGORIES':
        print("\nThe categories analysed by this model were :")
        d2 = d[1][1:-1].split(",")
        for d2x in d2:
          print(d2x.strip())
          aList.append(d2x) 
      if str(d[0]) == 'Row':
        print("\nExample data used for model generation was :")
        if int(blockSize) > 0:
          print("Blocksize - ",blockSize)
        if int(overlap) > 0:
          print("Overlap - ",overlap)
        print(d[1])
      
# After showing the user the categories the model was trained on, ask them if they wish to continue processing.  
  aList = [item.strip('"') for item in aList]
  aList = [item.strip(' ') for item in aList]
  aList = [item.replace("'", "") for item in aList]
  
  checkIfContinue()

  return aList, blockSize, overlap

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# For pre-processing physiological data changes are made if the mean data value over one data block differs from the mean value for a period 2 blocks earlier |
# by more than a given percentage. Get the user to igaussianput the percentage difference they wish to use. Block length can be one minute, a specified number of    |
# seconds, or a specified number of records.                                                                                                                  |
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPercent(txt,minP,maxP,defaultP):
  i = -1
  while i < 0:
    i = input(txt)
    if len(i) == 0:
      i = defaultP
    elif isInt(i) or isFloat(i):
      i = float(i)
      if (i < minP) or (i > maxP) :
        i = -1
      else:  
        done = True
    else:
      i = -1
  return i

#---------------------------------------------------------------------------------
# Get an integer input value from the user, with min, max and default specified. |
#---------------------------------------------------------------------------------
def getIntegerInput(txt,minVal,maxVal,defaultVal):
  i = -1
  while i < 0:
    i = input(txt)
    if len(i) == 0:
      i = defaultVal
    elif isInt(i):
      i = int(i)
      if (i < minVal) or (i > maxVal) :
        i = -1
      else:  
        done = True
    else:
      i = -1
  return i

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# The user enters mouse left clicks on a Matplotlib plot of input data to indicate start/stop/transition times, and concludes with a mouse right click. |
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def getStartStopTimes(trimTimes,tellText,startOnly):
  global xp, plt
# 'plt.ginput' gets user inputs from the plot (mouse clicks - left click adds a value to the output, backspace/delete removes a value,
# and right click terminates inputs).
# If 'trimTimes' is True the user is selecting start and end times of the data of interest - there must be exactly two left clicks.
# If startOnly is True then a start time only must be selected - one left click.
  tellme(tellText)
  xp = ""
  if trimTimes:
    if startOnly:
      while len(xp) != 1:
        xp = plt.ginput(0,timeout=-1,mouse_add=1, mouse_pop=2, mouse_stop=3)
        if len(xp) != 1:
          print("\nYou must left click on one point only - the start time of the data of interest. Then right click.")
    else:
      while len(xp) != 2:
        xp = plt.ginput(0,timeout=-1,mouse_add=1, mouse_pop=2, mouse_stop=3)
        if len(xp) != 2:
          print("\nYou must left click on two points - the start and end times of the data of interest. Then right click.")
  else:  
# If 'trimTimes' is False the user is manually labelling data. There must be a minimum of two left clicks, but often there should
# be more (the user will have performed more than one label during the time period covered by the data file). If they've only
# done two left clicks check with them that's what they meant to do.  
    while len(xp) < 2:
      xp = plt.ginput(0,timeout=-1,mouse_add=1, mouse_pop=2, mouse_stop=3)
      if len(xp) == 2:
        if not getYNInput("\nAre you sure you've selected all the label transitions (Y/N) - "):
          xp = []

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# The magnify utility can be used on a plot when the user is selecting data. If it has been used y-values well above/below the other clicks entered should have been used,  |
# so the magnifier clicks can be discarded. Ask the user for the y-values that determine magnifier clicks, and remove clicks above /below these values.                     |
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def procMagnifierClicks():
  global xp, plt_y_min, plt_y_max
  yMax, yMin = 0, 0
  print("\n Enter the y-values above/below which clicks should be ignored (because they were used for magnifying)")
  while yMax == 0:
    txt = "\nEnter y-value above which clicks are ignored (below " + str(plt_y_max) + ") : "
    yMax = input(txt)
    if not (isInt(yMax) or isFloat(yMax)):
      yMax = 0
    else:
      if float(yMax) > plt_y_max:
        yMax = 0            
  while yMin == 0:
    txt = "\nEnter y-value below which clicks are ignored (above " + str(plt_y_min) + ") : "
    yMin = input(txt)
    if not (isInt(yMin) or isFloat(yMin)):
      yMin = 0
    else:  
      if float(yMin) < plt_y_min:
        yMin = 0            
            
# The y-value of clicks is held in the second element of each instance of 'xp'
  yMax = float(yMax)
  yMin = float(yMin)    
  ind = 0        
  while ind < len(xp):
    if (float(xp[ind][1]) > yMax) or (float(xp[ind][1]) < yMin):
      print("Magnifier click discarded - ",xp[ind])
      xp.pop(ind)
    ind+=1  

#---------------------------------------------------------------------------------------------------------------------------------
# After the user has clicked on a plot to select data for particular time periods, find the start and stop times of each period. |
#---------------------------------------------------------------------------------------------------------------------------------
def procStartStopTimes():
  global pds, startTime, stopTime, dForm, xp 
# Get the start and end times of the data of interest (in the right datetime format). When reading through a data file these are used
# to decide when to start and stop processing data records.
  first = True  
  pds = []
  ind = 0
  
# 'xp' contains the x and y values of the user clicks, with the x-values (timestamps) in the first element xp[ind][0]
# Put a list of start/stop times into 'pds' for displaying to the user.
  xp = sorted(xp)
  while ind < len(xp):
    dt = int(xp[ind][0] * 86400)
    timestamp = datetime.utcfromtimestamp(dt)    
    tm = timestamp.strftime(dForm)
    if first:
      first = False
      startTime = tm
      strt = tm
    else:
      px = strt + " - " + tm
      strt = tm
      pds.append(px)       
    ind+=1
    
  stopTime = tm

#-------------------------------------------------------------------------------------------------------------------------------------------
# Ask the user which dataframe columns should be processed (plotted, included in the outfile/model etc). Show them an example data record. |
# They can specify single columns, or column ranges, with values separated by commas. eg 1-3,5 for columns 1, 2, 3 and 5.                  |
#-------------------------------------------------------------------------------------------------------------------------------------------
def selectColumns(inRec,inText,minNum):
  global numCols
  if numCols == 1:
    return [1]
  print("\nExample data record :")
  print(inRec)
  print(" ")
  colNums = []
  while len(colNums) == 0:
    inCols = input(inText)
    if len(inCols) == 0:
      colNums = list(range(1, numCols))
      return colNums
    for a, b in re.findall(r'(\d+):?-?(\d*)', inCols):
      if b=='':
        b = a
      if not isInt(a) or not isInt(b): 
        print("Invalid selection")
        colNums = []
      elif int(a) < 0 or int(b) < 0 or int(a) >= numCols or int(b) >= numCols:  
        print("Invalid selection")
        colNums = []
      else:          
        colNums.extend(range(int(a), int(b)+1))
    if len(colNums) < minNum:
      print("You must select at least " + str(minNum) + " columns.")
      colNums = []
  return colNums      

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# If the user amends the list of labels, allow them to save a copy of the source code (this program), containing the new list (in labelList).                         |
# The format of the source code needs to remain the same, with labelList followed by = and locationList followed by = determining where the label list is in the code.|
# The new file is saved using the current file name plus _copyx, where 'x' is the first positive integer such that the target file doesn't yet exist.                 |
# The source code builds a new sensorcodeConfigFile.txt if it doesn't exist, or doesn't contain the expected text.                                                    | 
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def createNewSourceCode(newLines):
# get the name of the running program
  myFile = os.path.abspath(__file__)
  f = open(myFile,'r')
  myCode = f.read()
  f.close()

# Find a file that doesn't exist using _copyx
  ix = 1
  while True:
    myFileCopy = myFile[:-3] + "_copy" + str(ix) + ".py"
    if not os.path.isfile(myFileCopy):
      break
    ix+=1  

# Delete the lines starting one line after labelList = and two lines before locationList = and replace with the new list of labels
  myCodeList = myCode.splitlines()  
  ix1 = [i for i, s in enumerate(myCodeList) if 'labelList =' in s]
  ix2 = [i for i, s in enumerate(myCodeList) if 'locationList =' in s]
  del myCodeList[ix1[0]+1:ix2[0]-2]
  myCodeList[ix1[0]+1:ix1[0]+1] = newLines
 
# Write the new file
  myCode = "\n".join(myCodeList) 
  f = open(myFileCopy,'w')
  f.write(myCode)
  f.close()
    
  print(myFile," copied to ",myFileCopy," with amended labels")    

#-------------------------------------------------------------
# Let the user delete labels from the current list of labels |
#-------------------------------------------------------------
def deleteLabelEntry(options):
  global changed
  lenOpt = len(options)
  removeInd = []
  print(" ")
  while True: 
    ix = input("Select label to delete (by number). CR to continue - ")
    if ix == "":
      break
    try:
      ix = int(ix)-1
      if (ix > -1) and (ix < lenOpt): 
        if ix in removeInd:
          print(options[ix]," has already been removed")
        else:
          print(options[ix]," removed")
          removeInd.append(ix)
    except:
      pass
  if len(removeInd) > 0:    
    for index in sorted(removeInd, reverse=True):
      changed = True
      del options[index]    
  return options

#--------------------------------------------------------
# Let the user add labels to the current list of labels |
#--------------------------------------------------------
def addLabelEntry(options):
  global changed
  while True: 
    addLabel = input("Enter label to add. CR to continue - ")
    if addLabel == "":
      break
    try:
      optionsUpper = list(map(str.upper,options))
      if addLabel.upper() in optionsUpper:
        print(addLabel," is already in the label list")
      else:
        options.insert(-1,addLabel)
        changed = True
    except:
      pass
  return options

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Append labels to data defined by time periods chosen by the user from a plot.                                                                                |
# Let the user amend the list of labels available for labelling data.                                                                                          |
# Make sure 'Other' is always the last label in the list. Delete any 'Other' that is not at the end of the list.                                               |
# 'Other' is used to skip chunks of data when processing.                                                                                                      |                                          
# Update sensorcodeConfigFile.txt if the list of labels has changed, and create a copy of the source code with the new labels if requested by the user.        |     
# If the user has selected several time periods from a plot they may have chosen time slices that they wish to keep, separated by time slices to be discarded. |
# Allow every 2nd time slice to be discarded automatically by labelling it as 'Other', without the user having to do this.                                     |                            |
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLabelsFromUser():
  global pds, startTime, ivals, dForm, uniqueLabel, options, configFile, labelList, changed, configChange

  print(" ")
  options = setupList("Label")
  for idx, element in enumerate(options):
    print("{}) {}".format(idx+1,element))
    
  changed = False
  print(" ")
  while True:
    procLabel = input("\nAdd (A)/Delete (D) labels. CR to continue - ").upper()
    if procLabel == "":  
      break
      
    if procLabel == "D":  
      options = deleteLabelEntry(options)
          
    if procLabel == "A":  
      options = addLabelEntry(options)

# Add the label 'Other' if it isn't there
  if not "Other" in options:
    print("'Other' must always be the last option. Adding it.")
    options.append("Other")
    changed = True
  else:
    if not options[-1] == "Other":
      options.append("Other")
      changed = True
    while options.count("Other") > 1:
      del options[options.index("Other")]  
      changed == True      

# Update the config file if the label list has changed
  if changed:
    os.remove(configFile)
    labelList = "\n"
    newLines = []
    for op in options:
      newLine = "               Label - " + op + "\n"
      newLines.append(newLine[0:-1])
      labelList+=newLine   
    getConfigs("User update")
    configChange = True

# Create a copy of the source code with the new labels, if requested
    if getYNInput("\nCreate copy of source code containing new labels? (Y/N) - "):
      createNewSourceCode(newLines)    

# If the user has selected more than one time slice (with more than two left clicks), ask them if they want to skip every 2nd one 
  skipAlternate, skip = False, False  
  if len(pds) > 2:
    if getYNInput("\nSkip every second time period as it is to be discarded? (Y/N) - "):
      skipAlternate, skip = True, True

# Show the user the list of available labels
  print(" ")
  for idx, element in enumerate(options):
    print("{}) {}".format(idx+1,element))

# Get the user to associate a label with each time slice they selected from the plot. If they asked to automatically skip every 2nd one, assign 'Other' to these slices.  
  ind = 0  
  print("\nSelect label (by number) for each time period - \n")  
  uniqueLabel = []
  for px in pds:
    done = False
    if skipAlternate:
      skip = not skip
    while not done: 
      if skip:
        i = len(options)
      else:
        txt = px + " - select label (by number) - "    
        i = input(txt)
      try:
        if 0 < int(i) < (len(options)+1):
          done = True
          indx = len(startTime)+3
          endTime = px[indx:]
          ivals[ind][0] = datetime.strptime(endTime,dForm)
          ivals[ind][1] = options[int(i)-1]
          if not ivals[ind][1] in uniqueLabel:
            uniqueLabel.append(ivals[ind][1])
          ind += 1 
        else:  
          print("Invalid selection")        
      except:
        print("Invalid selection")
        pass

#-----------------------------------------------------------------------------------------------------------------------------------------------------------  
# Display a plot of the data, and get time slices/start and end times/a starttime from the plot by the user left clicking on it, depending on the function |
# the code is being run for. Apply scaling to the displayed data if requested.                                                                             |
#   The user left clicks the start time, then left clicks the end time, then right clicks.                                                                 |  
#-----------------------------------------------------------------------------------------------------------------------------------------------------------  
def plotData(df,sTime,eTime,trimTimes,startOnly,tellText):
  global startTime, stopTime, dForm, plt_y_min, plt_y_max, scalePlot, dfScaledPlot, xp, dfNoScale, twoOutputs
  
  plt.rcParams["figure.figsize"] = [14.50, 6.50]
  plt.rcParams["figure.autolayout"] = True
  
  print("\nPlease wait, plotting data ...")
  if scalePlot:
    dfToPlot = dfScaledPlot
  else:
    dfToPlot = df

# Plot all data, or a time slice of it, depending on function.    
  if sTime == 0:
    dfToPlot.set_index('Time').plot()
  else:
    dfToPlot.loc[(dfToPlot['Time'] >= sTime) & (dfToPlot['Time'] <= eTime)].set_index('Time').plot()

# Display datetimes vertically on the x-axis (otherwise they take up too much room)      
  plt.xticks(rotation=90)
  plt.minorticks_on()
# Put gridlines on the plot to make it easier for the user to determine when activities change  
  plt.grid(b=True, which='major', axis='x', color='0.65', linestyle='-', lw = 1)  
  plt.grid(b=True, which='minor', axis='x', color='0.65', linestyle='--', lw = 1)  
  axes = plt.gca()
  plt_y_min, plt_y_max = axes.get_ylim()

# Get left clicks from the user, defining time periods
  getStartStopTimes(trimTimes,tellText,startOnly)     
  plt.close()
  
# If the user used the magnifier tool on the plot there will be clicks (used to select areas of the plot to magnify) that were not for time slice selection.
# The user should have clicked on y-values well above/below the values clicked when selecting time slices, when they used the magnifier. We'll discard 
# clicks with y-values above/below values specified by the user.
  if len(xp) > 2:
    if getYNInput("\nWas the magnifier tool used (Y/N) - "):
      procMagnifierClicks()
            
# Get the start and end times of the data of interest (in the right datetime format). When reading through a data file these are used
# to decide when to start and stop processing data records.
  procStartStopTimes()

# Convert start and end times to timestamps with the right format.  
  sTime1 = datetime.strptime(startTime,dForm)
  eTime1 = datetime.strptime(stopTime,dForm)

# Set the dataframe to contain just the records within the time slice selected by the user from the plot.  
  if startOnly:
    df = df.loc[(df['Time'] >= sTime1)]
    if twoOutputs:
      dfNoScale = dfNoScale.loc[(dfNoScale['Time'] >= sTime1)]
  else:
    df = df.loc[(df['Time'] >= sTime1) & (df['Time'] < eTime1)]
    if twoOutputs:
      dfNoScale = dfNoScale.loc[(dfNoScale['Time'] >= sTime1) & (dfNoScale['Time'] < eTime1)]
  
# If the user was selecting the start/stop times of the data of interest that's now been done, so return.
  if trimTimes:
    return df

# The user is labelling data. Get the labels to append to each time slice of the data, as selected by the user from the plot
  getLabelsFromUser()
  
  return df
  
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Plot data produced by the function selected by the user. Some plots provide a separate scale on the right hand y-axis to give a more appropriate display than using       |
# one scale on one y-axis provides. For example, if unlabelled data has been labelled, the label values will be integers starting from '1', but the data may be eg integers |
# in the region of 40 or above (for a heartrate). The label values will be much clearer when plotted with a second scale.                                                   | 
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def plotData2(df,twoYLabels):
  global numericCols
  fig,ax = plt.subplots()

# Provide a set of colours for different lines in the plot  
  colorMix = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
              (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
              (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
              (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
              (0.4, 0.6509803921568628, 0.11764705882352941),
              (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
              (0.6509803921568628, 0.4627450980392157, 0.11372549019607843),
              (0.4, 0.4, 0.4)]  
  plt.rcParams["figure.figsize"] = [14.50, 6.50]
  plt.rcParams["figure.autolayout"] = True
  plt.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colorMix)

  df.set_index('Time')
  
  ax.plot(df.iloc[:,0],df.iloc[:,numericCols[1:]])
  ax.set_xlabel("Time", fontsize = 10)
  ax.set_ylabel("Value",fontsize = 10,color="blue")
  
# Create a 2nd y-axis if required  
  if twoYLabels:
    ax2=ax.twinx()
    ax2._get_lines.prop_cycler = ax._get_lines.prop_cycler
    ax2.plot(df.iloc[:,0],df.iloc[:,-1])
    ax2.set_ylabel("Label",fontsize=10)
  
  plt.xticks(rotation=90)
  plt.minorticks_on()
  plt.grid(b=True, which='major', axis='x', color='0.65', linestyle='-', lw = 1)  
  plt.grid(b=True, which='minor', axis='x', color='0.65', linestyle='--', lw = 1)  
  plt.show()

#------------------------------------------------------
# Apply a set format to a timestamp (held in 'dForm') |
#------------------------------------------------------
def setDatetimeFormat(inString,dForm):
  return parse(str(inString)).strftime(dForm)

#---------------------------------------------------------------------
# Get the timestamps of the first and last records in the dataframe. |
#---------------------------------------------------------------------
def getFirstLastRecords(df):
  firstRecord = df.iloc[0,0]
  lastRecord = df.iloc[-1,0]
  if not isDatetime(lastRecord):
    print("\The selected input file does not have a datetime as the first element in a record.")
    print(helpText) 
    exit()  
  return firstRecord, lastRecord 

#-----------------------------------------------------------------------------------
# Ask the user how many records they wish to retain per second from the input file | 
#-----------------------------------------------------------------------------------
def getPerSec(freq):
    ok = False
    while not ok:    
      try:
        perSec = int(input("Specify number of readings to retain on average per second (min 5) - "))
        if (perSec > 4) and (perSec <= freq):
          ok = True
          return(perSec)
      except ValueError:
        ok = False
        
#-------------------------------------------------------------------------------------------------------------------
# For manual labelling of an unlabelled file.
# Ask the user for the subjectid (eg the initials of the person who was wearing a sensor). This is incorporated in | 
# the summary file, and may be a useful piece of information to have when analysing results.                       |
#-------------------------------------------------------------------------------------------------------------------     
def getSubjectId():
    ok = False
    while not ok:    
        subjectId = input("\nEnter subject id (eg initials) - ")
        if len(subjectId) > 0:
          ok = True
          return(subjectId)

#----------------------------------------------------------------------------------------------------------------------------
# Check if a file exists. If this is for a file being written to, and it does exist, ask the user how they wish to proceed. |
#----------------------------------------------------------------------------------------------------------------------------
def checkFileExists(inFile,appendAllowed,readFile):
  if not os.path.isfile(inFile):
    if readFile:
      print("\nFile ",inFile," does not exist.")
    return "N"
  if readFile:
    return "Y"  
  print(" ")  
  while True:
    if appendAllowed:
      txt = inFile + "already exists. Overwrite it (O), Append to it(A), choose another file (C) or stop (S) : "
    else:  
      txt = inFile + " already exists. Overwrite it (O), choose another file (C) or stop (S) : "    
    response = input(txt).upper()  
    if response == "S":
      print("\nTerminating ...")
      exit()
    if response == "O":
      os.remove(inFile)
    if (response == "A" and appendAllowed) or response == "O" or response == "C":
      return response

#-------------------------------------------------------------------------------------------------------------------------------
# Check if a file exists, and if it does delete it, if required. Do not include an append otion (unlike for 'checkFileExists') |
# for the user response if it does exist.                                                                                      |
#-------------------------------------------------------------------------------------------------------------------------------
def checkSpecificFileExists(inFile, check):
  if os.path.isfile(inFile) and not check:
    os.remove(inFile)
  if not os.path.isfile(inFile):
    return False
  print(" ")
  while True:
    txt = inFile + " already exists. Overwrite it (O), choose another folder (C) or stop (S) : "    
    response = input(txt).upper()  
    if response == "S":
      print("\nTerminating ...")
      exit()
    if response == "O":
      os.remove(inFile)
      return False
    if response == "C":
      return True
 
#------------------------------------------------------------------------------------------------------------------
# Group together data values into blocks of 'blockSize', and overlap blocks by 'blockSize - step' records.        | 
# Assign the most common label (from 'stats.mode') from the labels for all the records in a block, to that block. |
# These blocks are fed into a neural network for it to try and figure out patterns in the data values from        |
# training data to predict labels for test data or unlabelled data.                                               |
#------------------------------------------------------------------------------------------------------------------
def create_dataset(X, y, blockSize=1, step=1):
  Xs, ys = [], []
  for i in range(0, len(X) - blockSize, step):
    v = X.iloc[i:(i + blockSize)].values
    labels = y.iloc[i: i + blockSize]
    Xs.append(v)
# stats.mode returns the most common value (of activities)in the array (subset of x,y,z values and the associated label)
    ys.append(stats.mode(labels)[0][0])
  return np.array(Xs), np.array(ys).reshape(-1, 1)
    
#---------------------------------------------------------------------------------------------------------------------
# When using a neural network model to predict labels from data values, group these values into blocks with the same |
# number of records, and the same overlap between blocks, as were used when the model was created.                   |
#---------------------------------------------------------------------------------------------------------------------
def create_dataset2(X, blockSize=1, step=1):
  Xs = []
  for i in range(0, len(X) - blockSize, step):
    v = X.iloc[i:(i + blockSize)].values
    Xs.append(v)
  return np.array(Xs)

#--------------------------------------------------------------------------------------------------------------------------------------
# kMeans and keras (the neural network) algorithms require their inputs to be numeric. The label types (eg running, jumping etc) are  |
# converted into numeric values to create these models. When they are used to predict labels for an unlabelled file they output       |
# numbers rather than text for the label type. To create a labelled file from the model predictions the user is presented with a      |
# plot of the original data and predicted labels from which they associate the numerical label value with the text value for          |
# the label (eg 'walking').                                                                                                           |
#--------------------------------------------------------------------------------------------------------------------------------------   
def getLabelMap(aList,uniqueLabel,activities):
  print(" ")
  ixx = len(aList)*[-1]
  for a in uniqueLabel:
    txt = "Plot value " + str(a) + " - "
    ix = -1
    while ix < 0:
      try:
        ix = int(input(txt))
        if ix < 0 or ix > (len(aList)-1):
          print("You must enter a number between 0 and ",str(len(aList)-1))    
          ix = -1
        if ix in ixx:
          print("You have already selected this label")    
          ix = -1
        if ix > -1:
          ixx[a] = ix
      except ValueError:
        print("You must enter a number between 0 and ",str(len(aList)-1))    
        ix = -1  
        
  actualAct = []
  for val in activities:
    actualAct.append(aList[ixx[val]])
      
  return actualAct        

#-------------------------------------------------------------------------------------------------------------------------------------------
# When a model is created the list of labels it was created from is written (in this function) into a file called 'activities' in          |
# the same folder as the model is created. If a user subsequently uses this model to label an unlabelled file (eg from a sensor) they are  | 
# shown which labels the model was created with - as a check that this is an appropriate model to use for labelling the file (by reading   |
# the 'activities' file).                                                                                                                  |
# When building a Keras Neural Network model the data input to the model is clumped together into blocks, and blocks are overlapped. Block |
# size and overlap are held in 'blockSize' and 'overlap' respectively. These are also saved, along with a sample row of data.              |                                                                                                                |
#-------------------------------------------------------------------------------------------------------------------------------------------
def writeActivitiesFile(actFile,blockSize,overlap,activities):
  global dForm, df
  with open(actFile, 'w') as f: 
    write = csv.writer(f) 
    write.writerow(["dForm",dForm])   
    write.writerow(["BlockSize",blockSize])   
    write.writerow(["Overlap",overlap])   
    write.writerow(["Categories",activities])   
    write.writerow(["Row",df.iloc[1].values.flatten().tolist()])      
  f.close()  

  
#---------------------------------------------------------------------------------------------------------------------------------
# When a model is used to predict labels for an unlabelled file, eg from a sensor, show the user a text summary of the predicted |
# labels, with the duration for each label block, eg                                                                             |
# clap - 0 days 00:00:03                                                                                                         |
# walk - 0 days 00:16:20                                                                                                         |
# clap - 0 days 00:00:04                                                                                                         |
# walk - 0 days 00:09:24                                                                                                         |
# jump - 0 days 00:02:15                                                                                                         |
# clap - 0 days 00:00:03                                                                                                         |
#---------------------------------------------------------------------------------------------------------------------------------
def predictedLabelSummary(activities,uniqueLabel,df):
  print("\nPredicted label summary :\n")
  startInd, endInd = 0, 0
  acPrev = activities[0]
  actNums = []
 
  for ac in activities:
    actNums.append(uniqueLabel.index(ac))
    if ac != acPrev:
      print(acPrev," - ",df.iloc[(endInd-1),0] - df.iloc[startInd,0])
      acPrev = ac
      startInd = endInd
    endInd+=1
  if endInd > startInd:
    print(acPrev," - ",df.iloc[(endInd-1),0] - df.iloc[startInd,0])
  return actNums  
 
#------------------------------------------------------------------------------------------------------------------------------------------
# Use kMeans clusters to predict the label for each row in an output file.                                                                |
# Compare with the actual labels.                                                                                                         |
# Explanation - https://www.datacamp.com/tutorial/k-means-clustering-python                                                               |
# The parameters that may be useful to vary, or definitely must be set are :                                                              |
#   n_clusters : we will set this to the number of different labels in the input data file. We aim to assign each data point to one of    |
#     these labels, so this is the number of clusters we want.                                                                            |
#   max_iter - the maximum number of iterations performed.                                                                                |
#    From - https://stats.stackexchange.com/questions/261836/k-means-how-many-iterations-in-practical-situations                          |
#    in all practical situations a maximum of 20-50 is sufficient. The default value is 300 so we'll simply leave it at that.             |
#   n_init - the number of times the algorithm is run with different centroid seeds. Default is 10.                                       |
#   tol - the relative tolerance of the difference in cluster centres of two consecutive iterations to declare convergence. Default 1e-4. |
# Other parameters are largely concerned with efficiency/memory usage.                                                                    |
# After creating the model, store it (in a place specified by the user), along with an 'activities' file (containing a list of the        |
# activities analysed.                                                                                                                    |
#------------------------------------------------------------------------------------------------------------------------------------------
def kmeansAnalysis(xfilename):
  global targetCol, numericCols
  print("df.iloc[0:4] - ",df.iloc[0:4])
  print("targetCol - ",targetCol)
  actList = df.iloc[:,targetCol].values.tolist()
  activities = list(set(actList))  
  numact = len(activities)

# The model outputs predictions as numeric values. Compare all combinations of the actual values held in the input file against 
# the predictions made by the model to see which provides the best fit. eg if the input file contained :
# clap, clap, walk upstairs, walk upstairs, walk upstairs, clap, clap, walk downstairs, walk downstairs, walk downstairs, clap, clap
# and the model predictions were :
# 0, 1, 1, 1, 0, 2, 2, 2, 0, 1, 0
# we see how many matches are made for eg - 
# 0 = clap, 1 = walk upstairs, 2 = walk downstairs 
# 0 = clap, 2 = walk upstairs, 1 = walk downstairs
# 1 = clap, 0 = walk upstairs, 2 = walk downstairs 
# etc, checking all combinations and outputing the one that gives the most matches with trhe actual data.

  itx = []
  for item in permutations(range(numact), numact): 
    itx.append(item)
  
  X = np.array(df.iloc[:,numericCols])  
 
  kmeans = KMeans(n_clusters=numact, random_state=0).fit(X)
  
  acts = smoothActivities(kmeans.labels_)  
  
  maxMatches = 0
  for itxx in itx:
    ind = 0
    mtch = 0
    for la in acts:
      for ix in range(numact):
        if (activities[ix] == actList[ind]) and (la == itxx[ix]):
          mtch += 1
      ind+=1
    if mtch > maxMatches:
      maxMatches = mtch
      bestMatch = itxx
      
  print("Bestmatch - ",bestMatch)
  print("Matches - ",maxMatches,"/",ind)  
  print(round((maxMatches/ind)*100,1),"% accuracy")

# Save the model in a folder specified by the user, along with an 'activities' file showing the labels used to generate the model 
  defaultFolder = os.getcwd() 
  while True:    
    folder = selectFolder(defaultFolder,"\nSelect the folder to contain the kMeans Model; (D) for - " + defaultFolder + ", or select folder (S) (D/S) -  ")
    pklFile = folder + "/kMeans.pkl"
    if checkSpecificFileExists(pklFile,True):    
      continue
    actFile = folder + "/activities.csv" 
    if checkSpecificFileExists(actFile,False):    
      break
    break
    
  print("\nSaving model\n")
  pickle.dump(kmeans, open(pklFile, "wb"))
  writeActivitiesFile(actFile,0,0,activities)

#--------------------------------------------------------------------------------------------------------------------------
# Combine multiple copies of a machine learning model, that have been trained independently, to produce an average model. |
# Check the resultant model against the test data and show the user it's accuracy (how well predicted labels match actual |
# labels in the test data).                                                                                               |
# Save the model (to a folder that's been specified by the user).                                                         |
#--------------------------------------------------------------------------------------------------------------------------  
def baggingModelProc(filename,bagged_mod,modName,mod3,X_train, y_train,X_test,y_test,outFileEnd,folder):
  bagging_model = BaggingClassifier(bagged_mod, n_estimators=100)
  bagging_model.fit(X_train, y_train)

# Pass the test data to the trained model to obtain predictions (of label), and compare the accuracy with the actual label values  
  predictedAct = bagging_model.predict(X_test)
  accuracy = round(accuracy_score(y_test, predictedAct) * 100,1)
  print(modName," accuracy - ",accuracy) 

# Save the model 
  filename = folder + '/' + mod3 + '_' + outFileEnd 
  print("Saving model to ",filename)  
  pickle.dump(bagging_model, open(filename, 'wb'))

#---------------------------------------------------------------------------------------------------------------------------------------       
# Create 5 different machine learning models, each one trained against a data file that has been manually labelled by a user (based on |
# knowing what the actual labels were when the data file was being created).                                                           |
# Each model has inputs (called hyperparameters) that can be varied to try to maximise the accuracy of predictions.                    |
# The 'gridsearch' utility evaluates a model for each combination of these inputs, within specified ranges, to find the optimum values |
# (in terms of prediction accuracy). It uses randomly selected partitions of the data to assess each combination.                      |
# Each model is then trained against a 70% portion of the input file, with these optimum parameters, and then assessed for accuracy    |
# against a 30% proportion of the file.                                                                                                |
# The user is shown the accuracy of the model (as measured against the test data), and the model is saved (at a location specified by  |
# the user).                                                                                                                           |
# Information from - https://machinelearningmastery.com/evaluate-machine-learning-algorithms-for-human-activity-recognition/           |
#---------------------------------------------------------------------------------------------------------------------------------------        
def machineLearnAnalysis (xfilename):
  global df, numericCols, targetCol, uniqueLabel
  print("""
Select folder for saving Machine Learning models to.
Each model will be saved to a file in this folder using a filename made up of an abbreviation for the model and the
name of the input file from which the model is generated.
eg If the input file is 80933_0000000004LWNS.csv, then the following saved model files will be created :
  knn_80933_0000000004LWNS.sav (k-Nearest-Neighbour)
  rft_80933_0000000004LWNS.sav (Random_Forest)
  dtc_80933_0000000004LWNS.sav (Decision_Tree)
  svc_80933_0000000004LWNS.sav (Support_Vector_Machine)
  gnb_80933_0000000004LWNS.sav (GaussianNB)
  """)

# get the output folder  
  defaultFolder = os.getcwd() 
  while True:    
    folder = selectFolder(defaultFolder,"\nSelect the folder to contain the Machine Learning Models; (D) for - " + defaultFolder + ", or select folder (S) (D/S) -  ")
    actFile = folder + "/activities.csv" 
    if not checkSpecificFileExists(actFile,True):    
      break
  outFileEnd = os.path.basename(xfilename)[:-4] + ".sav"
   
  print("\nPlease wait, producing machine learning models ...\n")
  
# Remove the timestamp column - it is not used by these algorithms. 'targetCol' is the column containing the labels (as specified by the user)
  df = df.drop("Time", axis=1)
  numericCols = [x-1 for x in numericCols]
  targetCol-=1
# Select 20% of the dataframe, keeping the proportion of each label the same as for the whole dataframe.
# This will be used for tuning hyperparameters for algorithms that take a long time to get the tuning values for.  
  part_df = df.groupby(df.columns[targetCol]).apply(lambda x: x.sample(frac=0.2))

# The independent (numeric) variables are loaded into 'X', and the dependent variable (label - what we're trying to predict) is loaded into 'y'
  X = df.iloc[:,numericCols].copy()    
  X = X.values
  y = df.iloc[:,targetCol].copy()      
  y = y.values
  
# Split the data into train and test blocks, 70% train and 30% test 
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

  pX = part_df.iloc[:,numericCols].copy()    
  pX = pX.values
  py = part_df.iloc[:,targetCol].copy()      
  py = py.values
  
# Split the partial data blocks into train and test blocks, 70% train and 30% test 
  pX_train, pX_test, py_train, py_test = train_test_split(pX, py, test_size=0.3)
# Random forest information - https://medium.com/analytics-vidhya/random-forest-classifier-and-its-hyperparameters-8467bec755f6 
# Tuning - https://medium.com/all-things-ai/in-depth-parameter-tuning-for-random-forest-d67bb7e920d#:~:text=the%20test%20performance.-,max_depth,the%20training%20and%20test%20errors. 
  param_grid = {'n_estimators': [32,64,128], 'criterion': ['gini','entropy'],'min_samples_leaf': range(1,5,1),'min_samples_split': range(2,6,1),'max_features': ['auto', 'log2']}
# Find the optimum hyperparamaters for Random Forest
  gridsearch = GridSearchCV(RandomForestClassifier(),param_grid,cv=5,n_jobs=-1,verbose=0)
  gridsearch.fit(pX_train,py_train)
  best_ne = gridsearch.best_params_['n_estimators']  
  best_crit = gridsearch.best_params_['criterion']  
  best_msl = gridsearch.best_params_['min_samples_leaf']  
  best_mss = gridsearch.best_params_['min_samples_split']  
  best_mf = gridsearch.best_params_['max_features']  
  
# Train the Random Forest model
  rand_rfc = RandomForestClassifier(n_estimators=best_ne,criterion=best_crit,max_features=best_mf,min_samples_leaf=best_msl,min_samples_split=best_mss)
  rand_rfc.fit(X_train, y_train)

# Pass the test data to the trained model to obtain predictions (of label), and compare the accuracy with the actual label values  
  predictedAct = rand_rfc.predict(X_test)
  accuracy = round(accuracy_score(y_test, predictedAct) * 100,1)
  print("Random Forest Classifier accuracy - ",accuracy) 

# Save the trained model  
  filename = folder + '/rfc_' + outFileEnd
  print("Saving model to ",filename)  
  pickle.dump(rand_rfc, open(filename, 'wb'))
       
# k-Nearest neighbour is a supervised machine learning algorithm, based on the concept that data with similar characteristics are liable to 
# belong to the same categories (when aiming to categorize unseen data). 
# The two optional parameters that affect the accuracy of k-Nearest neighbour are how many neighbouring points are 
# taken into account, and whether or not the distance of neighbouring points from the point under consideration is weighted.
  parameters = {"n_neighbors": range(1, 50),"weights": ["uniform", "distance"]}
  gridsearch = GridSearchCV(KNeighborsClassifier(), parameters)
  gridsearch.fit(X_train, y_train)  
  best_k = gridsearch.best_params_["n_neighbors"]
  best_weights = gridsearch.best_params_["weights"]

# Bagging trains the model on different subsets of the training data, and combines predictions based on a combination of results. 
# Save the resulting model. 
  bagged_knn = KNeighborsClassifier(n_neighbors=best_k, weights=best_weights) 
  baggingModelProc(filename,bagged_knn,"k-Nearest Neighbour","knn",X_train,y_train,X_test,y_test,outFileEnd,folder)
  
# A decision tree builds a set of yes/no rules based on the training data to enable it to allocate a category (in this case) for unseen 
# data points (from the test data). The model determines the best set of rules to apply to maximise the accuracy of predictions based on 
# the target values (label type) contained in the training data. With each split an evaluation is made of the number of data points
# belonging to each class (label type here). 
# Explanation - https://towardsdatascience.com/decision-tree-classifier-explained-in-real-life-picking-a-vacation-destination-6226b2b60575

# Optimize (tune) the hyperparameters - see https://towardsdatascience.com/how-to-tune-a-decision-tree-f03721801680  
# Features of the tree that can be changed to affect accuracy are : 
#   the function used to measure the quality of the split
#   the depth of the tree (how many splits are made)
#   the minimum number of samples any branch can terminate with

  param_grid = [{'min_samples_leaf': range(1, 20)},{'min_samples_split': range(2, 40)}]

# Call the fit() method to perform the grid search using 3-fold cross-validation.
  gridsearch = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=3)  
  gridsearch.fit(X_train, y_train)

# Bagging trains the model on different subsets of the training data, and combines predictions based on a combination of results. 
# GridsearchCV will either return min_samples_leaf or min_samples_split. Use whichever it is as the tuning value. 
  if 'min_samples_leaf' in gridsearch.best_params_ :
    best_msl = gridsearch.best_params_['min_samples_leaf']  
    bagged_dtc = DecisionTreeClassifier(min_samples_leaf=best_msl)
  else:
    best_mss = gridsearch.best_params_['min_samples_split']  
    bagged_dtc = DecisionTreeClassifier(min_samples_split=best_mss)

  baggingModelProc(filename,bagged_dtc,"DecisionTreeClassifier","dtc",X_train,y_train,X_test,y_test,outFileEnd,folder)
  
# SVC is Support Vector Machine (SVM) algorithm applied for classification. SVM finds hyperplanes that distinctly classify data. A hyperplane
# acts as a decision boundary for classifying data points. The algorithm looks for the hyperplane that provides the greatest distance between 
# data points with different classifications on either side of it, so the separation between the 2 classes is as wide as possible.  
# This maximises the probability that unseen data points are assigned to the correct class.  
# Explanation - https://towardsdatascience.com/support-vector-machine-introduction-to-machine-learning-algorithms-934a444fca47  
# and - https://towardsdatascience.com/https-medium-com-pupalerushikesh-svm-f4b42800e989#:~:text=SVM%20or%20Support%20Vector%20Machine,separates%20the%20data%20into%20classes.
# The most commonly adjusted params (according to https://holypython.com/svm/support-vector-machine-optimization-parameters/) are :
#  Cfloat , kernel, degree, gamma, tol and cache_size.
# C - as 'c' increases the intricacy of the decision curve separating classes increases. More training points are classified correctly,
#     but generalisation decreases, which may result in poorer predictions for unseen data (overfitting). Default 1.0.
# Gamma - as this increases more weight is given to points close to the boundary potentially causing overfitting. A low value gives more 
#         weight to points further from the boundary, potentially underfitting. 
# kernel - the function type used to transform data to try to obtain the best distinction between classes. One of linear, poly, rbf,
#          sigmoid, precomputed. Default rbf (radial basis function).
# degree - only applies to 'poly'. Default 3.

  param_grid = {'C': [0.1,1, 10, 100]}
  
  gridsearch = GridSearchCV(LinearSVC(),param_grid,refit=True)
  gridsearch.fit(pX_train,py_train)
  best_C = gridsearch.best_params_['C']  

# Bagging trains the model on different subsets of the training data, and combines predictions based on a combination of results.  
  bagged_svc = LinearSVC(C=best_C)  
  baggingModelProc(filename,bagged_svc,"LinearSVC","svc",X_train,y_train,X_test,y_test,outFileEnd,folder)

#------------------------------------------------------------------------------------------------------------------------------------
# GaussianNB (Naive Bayes) assumes each parameter has an independent capacity to predict the output (label). The probability of the |
# output having a particular classification is obtained from the combination of the predictions for all the parameters.             |
# Explanation : https://pub.towardsai.net/gaussian-naive-bayes-explained-and-hands-on-with-scikit-learn-4183b8cb0e4c                 |
#------------------------------------------------------------------------------------------------------------------------------------ 
  
  params_NB = {'var_smoothing': np.logspace(0,-9, num=100)}
  gridsearch = GridSearchCV(GaussianNB(), param_grid=params_NB, cv=3, scoring='accuracy') 
  gridsearch.fit(X_train, y_train)

  best_vs = gridsearch.best_params_['var_smoothing']  

# Bagging trains the model on different subsets of the training data, and combines predictions based on a combination of results.  
  bagged_GNB = GaussianNB(var_smoothing=best_vs) 
  baggingModelProc(filename,bagged_GNB,"GaussianNB","gnb",X_train,y_train,X_test,y_test,outFileEnd,folder)
  
#  actFile = "activities.csv"
  writeActivitiesFile(actFile,0,0,uniqueLabel)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Load a (manually) labelled data file into a dataframe. Split it into train and test data sets for passing to a neural network model.                                       |
# Form blocks of data (defined by a time period specified by the user - default 2 second blocks), that are overlapped (by a percentage specified by the user - default 50%). |
# Convert the label values (held as text in the input file, eg 'walk upstairs') into numerical values, as required by the neural network.                                    |
# Info -  https://towardsdatascience.com/time-series-classification-for-human-activity-recognition-with-lstms-using-tensorflow-2-and-keras-b816431afdff                      |
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def loadDataset (xfilename):
  global X_train , X_test , y_train , y_test, headers2, perMinute, numCols, df, targetCol, colNums, numericCols
  
# The neural network seems to 'learn' best if the data are not in large blocks, all with the same label - if different labels are mixed up. Randomly 'shuffle' blocks
# of the dataframe, that are each 100th the size of the dataframe. We don't want to do too much record shuffling, otherwise data patterns will be lost.    
  dflen=len(df)
  maxRecs = 100
  numBlocks = int(dflen/maxRecs)
  sel = random.sample(range(numBlocks), numBlocks)
  data = []
  for s in sel:
    x1 = s*maxRecs
    x2 = x1+maxRecs
    xBlock = df.iloc[x1:x2].values.tolist()
    data.append(xBlock)
  flat = [x for sublist in data for x in sublist]

  headers2 = [f'Col {i}' for i in range(1,numCols)] 
  headers2.insert(0,"Time")
  df.columns = headers2
    
  df = pd.DataFrame(flat,columns=headers2)

# Split the dataframe into test and train entities - first 70% for training, last 30% for testing. Train and test 
# should contain examples of all activities.
  df_train, df_test = np.split(df, [int(.7*len(df))])

  columns = headers2[1:]
  df_train.loc[:, columns] = df_train[columns].to_numpy()
  df_test.loc[:, columns] = df_test[columns].to_numpy()
        
  firstRecord, lastRecord = getFirstLastRecords(df)

# Get the user to specify the length of time blocks that the data is split into in seconds
  if perMinute:
    blockSize = int(freq)
  else:
    i = 0
    while i == 0:
      i = input("\nEnter length of interval data is split into in seconds, eg 2.5 (CR for default = 2.0 seconds) : ")
      if len(i) == 0:
        i = 2
      elif isInt(i) or isFloat(i):
        i = float(i)
        done = True
      else:
        i = 0
    blockSize = int(i*freq)
  
 # Get the user to specify the percentage overlap between blocks of data
  percent = getPercent("\nEnter percentage overlap between blocks of data in the range 0 to 90 (CR for default = 50%) : ",0,90,50)
   
  print(" ") 
  overlap = int(blockSize - ((percent/100)*blockSize))
    
  X_train, y_train = create_dataset(
    df_train.iloc[:,numericCols],
    df_train.iloc[:,targetCol],
    blockSize,
    overlap
  )

  X_test, y_test = create_dataset(
    df_test.iloc[:,numericCols],
    df_test.iloc[:,targetCol],
    blockSize,
    overlap
  )    

# Convert the label values which are strings (eg 'walk upstairs') to numerical values for use in the predictive
# model (keras works with numbers rather than strings). An array is created so that the model doesn't interpret
# different labels as having greater numerical differences between them, eg there is no distinction for the
# difference in the numeric values representing 'walk upstairs' and 'clap' and 'walk downstairs' and 'clap'.
  enc = OneHotEncoder(handle_unknown='ignore', sparse=False)
  enc = enc.fit(y_train)
  y_train = enc.transform(y_train)
  y_test = enc.transform(y_test)
  
  return blockSize, overlap

#---------------------------------------------------------------------------------------------------------------------------------
# After a machine learning/neural network model has been run against an unlabelled file, create a new labelled file              |
# consisting of the input data, plus the predicted label for each data record.                                                   |
# If the predicted label from the model is numeric, get the user to specify the text value for each numeric output after showing | 
# them a plot of the input data and predicted activities.                                                                        |
# The user specifies where to create the labelled file.                                                                          |
#---------------------------------------------------------------------------------------------------------------------------------  
def produceLabelledFile(xfilename,getAssoc,aList,uniqueLabel,activities,txt):
  global df, numCols, headers, firstIsCsv, csvFile
  
  firstIsCsv = csvFile  

  if not getYNInput("Produce labelled file using these predictions? Y/N "):
    return
    
  defaultFolder = os.path.dirname(xfilename)
  folder = selectFolder(defaultFolder,"\nSelect the folder to create the output file in (D) for - " + defaultFolder + " or select folder (S) (D/S) - ")
  
  response = "C"
  while response == "C":
    predictedFile, fName = getNewFilename("",folder,"Enter output filename")
    response = checkFileExists(predictedFile,True,False)
  response = "C"
 
  if getAssoc:    
# The labels predicted by the model are numeric. Ask the user for the string equivalents.
    if len(uniqueLabel) == 1:
      actualAct = [aList[int(uniqueLabel[0])] for i in range(len(activities))]
    else:      
      print("\nSelect the actual label (by number) associated with the label values shown in the plot : \n")
      ind = 0
      for a in aList:
        print(ind," - ",a)
        ind+=1
      actualAct = getLabelMap(aList,uniqueLabel,activities) 
  else:
    actualAct = activities 

# Add the predicted labels to the dataframe
  df = df.head(len(actualAct))
  df['label'] = actualAct  

  numCols+=1
  headers = [f'Col {i}' for i in range(1,numCols)] 
  headers.insert(0,"Time")
  df.columns = headers
  column_names = headers     

# Produce an output file    
  writeOutputFile(df,True,predictedFile,True)

#--------------------------------------------------------------------------------------------------------------------------
# Determine the format of the input datetime field (input files must have a datetime as the first element in each record) |
#--------------------------------------------------------------------------------------------------------------------------
def findDateTimeFormat(inString):
  inString = str(inString)
  
# Break the datetime into date and time parts  
  pattern = r'[^a-zA-Z0-9\_]'
  joinChars = [*set(re.findall(pattern, (inString)))]
  joinChars.remove(" ")
  inString2 = ''.join(' ' if ch in joinChars else ch for ch in inString)  
  indices = [s.start() for s in re.finditer(' ', inString2)]
  inDate, inTime = inString[:indices[2]], inString[(indices[2]+1):] 

# Specify the date and time formats that are catered for  
  dforms = ["%Y%m%d","%d%m%Y","%m%d%Y","%Y%b%d","%d%b%Y","%b%d%Y"]
  tformats = ['%H.%M.%S','%H:%M:%S','%H.%M.%S.%f','%H:%M:%S.%f','%H.%M','%H:%M']
    
  dformats = []
  for df in dforms:
    for ix in range(len(joinChars)):
      match_string = df[0:2]+joinChars[ix]+df[2:4]+joinChars[ix]+df[4:6]
      dformats.append(match_string)

# Check which date and time formats are present in the input datetime. If the format for either is not matched, tell the user and stop (the code will need amending).  
  dFound = ""
  for dformat in dformats:
    try:
      datetime.strptime(inDate, dformat)
    except ValueError:
      dFound = ""
    else:
      dFound = dformat 
      break
  if dFound == "":    
    print("date didn't match with any known formats")
    exit()

  tFound = ""
  for tformat in tformats:
    try:
      datetime.strptime(inTime, tformat)
    except ValueError:
      tFound = ""
    else:
      tFound = tformat 
      break
  if tFound == "":    
    print("time didn't match with any known formats")
    exit()
  outForm = dFound+" "+tFound
  return outForm


#------------------------------------------------------------------------------------------------------------------------------------------
# Build a 'keras' neural network model using input data that has been manually labelled by the user.                                      |
# The input data is split into 70% training data, and 30% testing data (for evaluation of accuracy).                                      |
# Each set of data is split into overlapping blocks with a fixed time period  - the time period length and overlap % can be specified     |
# by the user - default 2 seconds and 50%.                                                                                                |
# A neural network consists of 'nodes' (to emulate neurons in a brain) with data being passed from one node to the next according to      |
# whether or not its value exceeds a certain threshold when subjected to a particular transformation. Blocks of data are combined and the | 
# model determines how well it is performing in terms of making predictions as compared to the actual target values.                      |
# An attempt was made to use 'gridsearch' as for the machine learning algorithms, to tune the hyper-parameters for the model,             |
# but this resulted in poor accuracy. A 'manual' tune process is performed here, by testing the accuracy of predictions                   |
# for a range of epochs (the number of times the data passes through the model) and a range of batch sizes (the number of data            |
# records passed from one node to the next).                                                                                              |
# A model is then built using the optimum epoch and batch size value, and saved to a location specified by the user.                      |
# Info - https://machinelearningmastery.com/evaluate-machine-learning-algorithms-for-human-activity-recognition/                          |
# Info on keras tuning - https://www.tensorflow.org/tutorials/keras/keras_tuner                                                           |
#------------------------------------------------------------------------------------------------------------------------------------------
def kerasAnalysis (xfilename):
  global X_train , X_test , y_train , y_test, df, uniqueLabel  
  tf.get_logger().setLevel('ERROR')

# Get the input file, loaded into overlapping blocks of data
  blockSize , overlap = loadDataset(xfilename)

# Create a deep learning keras model that accepts the inputs - numeric values and their associated labels
  model = tf.keras.Sequential()
  model.add(
# allow the model to take into account previous as well as subsequent values being passed to it
    tf.keras.layers.Bidirectional(
# LSTM (Long short-term memory) is a type of recurrent neural network (RNN) that uses past information over a relatively
# long time period (compared to some neural network models) for improving prediction accuracy.    
      tf.keras.layers.LSTM(
# Create 128 copies of the RNN that are initialised with different weights (multipliers for the input values - different 
# ones are used to try to get the bestmeans of matching input values (numeric) to output values (labels)       
          units=128,
# Tell the model the dimensions (how many rows and columns here) are in each chunk of information being passed to it          
          input_shape=[X_train.shape[1], X_train.shape[2]]
      )
    )
  )
# Dropout removes a proportion of inputs. This helps prevent the model from overfitting earlier inputs (trying to get 
# an exact match between inputs and output rather than an approximate one) at the expense of later inputs (which may 
# contain data features of relevance that are subdued or not present in earlier inputs).
  model.add(tf.keras.layers.Dropout(rate=0.5))
# A Rectified Linear Activation function (relu) is applied by the nodes (neurons) to determine output values. 'relu'
# outputs either the input value if it is greater than zero, or zero otherwise. This results in many zero outputs which
# reduce the size of the matrices being processed and has been determined to be an effective function for pattern
# recognition.
  model.add(tf.keras.layers.Dense(units=128, activation='relu'))
# 'softmax' converts a vector of output values to a probability distribution enabling the output result to be interpreted 
# in terms of probability.
  model.add(tf.keras.layers.Dense(y_train.shape[1], activation='softmax'))

# categorical_crossentropy is used for models predicting categories where there are multiple possible outputs (here 
# the labels might be eg walk upstairs, walk downstairs, clap, etc). It is a 'loss function' - it seeks to minimise a
# particular scalar value to make predictions as close to the true labels as possible.
# The optimizer is an algorithm that changes the weights and learning rate to minimise losses (maximise the accuracy
# of predictions)
# The metric measures the performance of the model. 'acc' is for how often the prediction matches the category.
  model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['acc']
  )

# Train the model for a fixed number of iterations (epochs) on the dataset (here, the numeric input values)
# batch_size is the number of input values passed into the model at a time. Different values should be tried to find
# the optimum value (best prediction rate) - there is not a formula for calculating the best batch_size to use.
# validation_split gives the fraction of training data used to validate the model - this proportion (here 10%) is
# set aside and used to assess how the model is performing after each epoch.
# shuffle is used to state whether or not the training data should be shuffledbefore being fed into the model. There is
# no benefit to doing that here - in fact the model may work better if values that are adjacent time-wise are kept in 
# correct order (for detecting repetitive patterns).
  eval_max = 0
  best_ix1 = 0
  best_ix2 = 0
    
  for ix1 in range(4,9):
    for ix2 in range(6,11):
      print("Checking epochs - ",ix1," batch_size - ",ix2)
      history = model.fit(X_train, y_train,epochs=ix1,batch_size=ix2,validation_split=0.1,shuffle=False,verbose=0)
# model.evaluate predicts outputs (here, for the test data) and computes all the metrics (we are interested in the
# accuracy of the label predictions).
      eval = model.evaluate(X_test, y_test)
      if eval[1] > eval_max:
        eval_max = eval[1]
        best_ix1 = ix1
        best_ix2 = ix2

  print("Best epochs - ",best_ix1)
  print("Best batch_size - ",best_ix2)
  print("Match - ",round(eval_max,3))

# After showing the user how well the model performed, ask if they wish to save it.  
  if not getYNInput("Save this Neural Network model? (Y/N) : "):
    return

  print("\nPlease wait, fitting the model ...")
  history = model.fit(X_train, y_train,epochs=best_ix1,batch_size=best_ix2,validation_split=0.1,shuffle=False,verbose=0)

# model.predict simply shows the predictions (for the test data), but not the accuracy
  
# Saving a trained Keras model (in files) for later use on other data :  
# https://www.tensorflow.org/tutorials/keras/save_and_load  
# Save the entire model as a SavedModel.

  defaultFolder = os.getcwd() 
  while True:    
    folder = selectFolder(defaultFolder,"\nSelect the folder to contain the Neural Network Model; (D) for - " + defaultFolder + ", or select folder (S) (D/S) -  ")
    modelFile = folder + "/saved_model.pb"
    if checkSpecificFileExists(modelFile,True):    
      continue
    actFile = folder + "/activities.csv" 
    if checkSpecificFileExists(actFile,False):    
      break
    break

  print("\nPlease wait, saving the model ...")
  model.save(folder)

# save the file showing what sort of data the model was created from.  
  actFile = folder + "/activities.csv" 
  writeActivitiesFile(actFile,blockSize,overlap,uniqueLabel)

#-------------------------------------------------------
# Get the user to select the folder containing a model |
#-------------------------------------------------------
def getModelFolder(modName,fName):
  ok = False
  txt = "\nSelect the folder containing the " + modName + " model - "
  txt2 = "\nThe two files " + fName + " and activities.csv must exist in the selected folder"
  while not ok:
    print(txt)
    root = Tk(); root.withdraw()
    directoryname = fd.askdirectory(title="select")    
    root.destroy()
    filename = directoryname + "/" + fName
    actFile = directoryname + "/activities.csv" 
    if not (os.path.exists(filename) and os.path.exists(actFile)):
      print(txt2)
    else:
      ok = True    
  return filename, actFile, directoryname    

#----------------------------------------------------------------------------------------------------------------------  
# Run a previously saved 'kmeans' machine learning model against an unlabelled file, and create a file containing the |
# original data plus the predicted label for each input record, if requested by the user.                             |
# The user selects the input file and location of the model to load.                                                  |
#----------------------------------------------------------------------------------------------------------------------  
def runSavedKmeans(xfilename):
  global df, firstIsCsv
  firstIsCsv = csvFile

# Get the user to select the folder containing the saved model - a separate Explorer window opens for selection
  filename, actFile, directoryname = getModelFolder("kMeans","kMeans.pkl")

# Show the user what activities were contained in the data that was used to create the model.  
  aList, blockSize , overlap = showModelActivities(actFile)

# Load the input data, for a time slice selected by the user (from a plot of the data)
  df = plotData(df,0,0,True,False,'Select the start and end times of the data of interest using mouse left-click. Finish input with mouse right-click. Remove entry with delete/backspace.')    

  X = df[df.columns[1:]] 

# load the model
  new_model = pickle.load(open(filename, 'rb'))

# Get the label predictions using the model
  predictedAct=new_model.predict(X)  

# 'Smooth' the predictions - for blocks of time set all the label values to the most common value for that period.
# The model might for example predict 1/10th of a second of clapping during a 10 second period of walking - it is assumed that such a prediction is probably incorrect,
# so amend it.
  activities = smoothActivities(predictedAct)  
  uniqueLabel = list(set(activities))

# Show the user a summary of predicted labels
  actNums = predictedLabelSummary(activities,uniqueLabel,df)

# Add the predictions to the dataframe
  df2 = df.copy()
  df2[-1] = activities  

  numericCols.insert(0,0)  

# Plot the input data plus predicted labels  
  plotData2(df2,True)

# Create an output file containing the original data plus predicted labels
  produceLabelledFile(xfilename,True,aList,uniqueLabel,activities,"km01Jul2022")


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------  
# Run a previously saved machine learning model against an unlabelled file, and create a file containing the original data plus th predicted label for each input record. |
# Any one of the 5 model types created by the code can be used - Random Forest, k-Nearest neighbour, support vector machine, decision trand GaussianNB.                   |
# The user selects the input file and location of the model to load.                                                                                                      |
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def runSavedML(xfilename):
  global df

# Get the user to select the file containing the saved model - a separate Explorer window opens for selection
  ok = False
  while not ok:
    print("\nSelect the file containing the model to be used")
    root = Tk(); root.withdraw()
    filename = fd.askopenfilename(filetypes=[("sav Files", "*.sav")])
    root.destroy()
    actFile = os.path.dirname(filename) + "/activities.csv"   
    if not os.path.exists(actFile):
      print("\nThe file activities.csv must exist in the same folder as the model. Please select another file or recreate the model using this code.")
    else:
      ok = True    

# Show the user what labels that were contained in the data that was used to create the model.  
  aList, blockSize , overlap = showModelActivities(actFile)

# Ask the user to select a time slice of the input file, from a plot. Remove the timestamp column.
  df = plotData(df,0,0,True,False,'Select the start and end times of the data of interest using mouse left-click. Finish input with mouse right-click. Remove entry with delete/backspace.')        
  X = df.drop("Time", axis=1)
  X = X.values
          
# load the model and get the label predictions
  loaded_model = pickle.load(open(filename, 'rb'))
  predictedAct = loaded_model.predict(X)
 
# 'Smooth' the predictions - for blocks ot fime set all the label values to the most common value for that period.
# The model might for example predict 1/10th of a second of clapping during a 10 second period of walking. Correct such anomalies.
  activities = smoothActivities(predictedAct)  
  uniqueLabel = list(set(activities))

# Get the user to associate predicted numeric values with actual labels (by showing them a plot of original data and predictions)
  actNums = predictedLabelSummary(activities,uniqueLabel,df)

# Add the labels to the dataframe
  df2 = df.copy()
  df2 = df2.head(len(activities))
  df2[-1] = activities    

  numericCols.insert(0,0)  
  df2.set_index('Time')
  
# Display a plot of the data and predicted labels
  plotData2(df2,True)

# Create an output file containing the original data predicted labels.  
  produceLabelledFile(xfilename,False,aList,uniqueLabel,activities,"ML01Jul2022")

#-------------------------------------------------------------------------------------------------------------------------------------  
# Run a previously saved keras (neural network) model against an unlabelled file, and create a file containing the original data plus the predicted label for each input record. 
# The user selects the input file and location of the model to load.
#-------------------------------------------------------------------------------------------------------------------------------------    
def runSavedKeras(xfilename):
  global df, dForm
  tf.get_logger().setLevel('ERROR')

# Get the user to select the folder containing the saved model - a separate Explorer window opens for selection
  filename, actFile, directoryname = getModelFolder("keras","saved_model.pb")

# Show the user what labels were contained in the data that was used to create the model.  
  aList, blockSize , overlap = showModelActivities(actFile)

# Get the user to select a time slice of the input file
  df = plotData(df,0,0,True,False,'Select the start and end times of the data of interest using mouse left-click. Finish input with mouse right-click. Remove entry with delete/backspace.')    
    
# Create blocks of overlapping data
  X_test = create_dataset2(df[df.columns[1:]],int(blockSize),1)

# load the model
  print("\nPlease wait. Loading model ...")
  new_model = tf.keras.models.load_model(directoryname)

# Get the label predictions
  predict_x=new_model.predict(X_test)  
  predictedAct=np.argmax(predict_x,axis=1)
  
# 'Smooth' the predictions - for blocks of time set all the label values to the most common value for that period.
# The model might for example predict 1/10th of a second of clapping during a 10 second period of walking - correct these anomalies.
  activities = smoothActivities(predictedAct)
  
  uniqueLabel = list(set(activities))
  
# Show the user a summary of predicted labels
  actNums = predictedLabelSummary(activities,uniqueLabel,df)

# Add the predicted labels to a dataframe
  df2 = df.copy()
  df2 = df2.head(len(activities))
  df2[-1] = activities    

  numericCols.insert(0,0)  
  df2.set_index('Time')

# Display a plot of the original data and the predicted labels     
  plotData2(df2,True)

# Create an output file containing the original data, plus predicted labels.  
  produceLabelledFile(xfilename,True,aList,uniqueLabel,activities,"NN01Jul2022")
  
#---------------------------------------------------------------------------------------------------------------------------------------------------------
# Append the label associated with the timestamp of the current record (held in 'ivals[ind][1]') to the record, then add it to 'outRecs'                 |
# (which will be written to the output file). If the label has changed from the record for the previous label, store the transition point, which is used |
# when building the summary file to determine the mean and standard deviation of numeric variables for each time period associated with a single label.  |
#---------------------------------------------------------------------------------------------------------------------------------------------------------
def createRecord(ind):
  global row, activities, newTime, firstAct, transVal, transition, numCols, getRms, outRecs
  outRec = [newTime]
  for i in range(1,numCols):
    outRec.append(row[i])
  if getRms:  
    outRec.append(round(svm,2))
  outRec.append(ivals[ind][1])
  activities.append(ivals[ind][1])  
  transVal+=1
  if firstAct:
    firstAct = False
  else:
    if activities[-1] != activities[-2]:
      transition.append(transVal)    
  outRecs.append(outRec)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# When labelling unlabelled data, ask the user if they wish to add a root mean squared value to the output file, and, if so, which input columns to generate it from. |
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def procRms():
  global getRms, rmsCols, headers2, df, numericCols
  getRms = False
  rmsCols = []  
  if len(numericCols) > 1:
    ok = False
    if getYNInput("\nCreate Root Mean Square values? (Y/N) : "):
      getRms = True
      done = False
      while not done:
        done = True
        if len(numericCols) > 2:
          rmsCols = selectColumns(df.iloc[0],"Select the columns to include in RMS value (first column is column 0). eg 2,3,4 or 2-4,6,7-9 (CR for all numeric columns) - ",2)
        if len(rmsCols) == 0:
          rmsCols = numericCols
        else:  
          for r in rmsCols:
            if not r in numericCols:
              print("You can only select numeric values for inclusion.")
              done = False

  if getRms:
   headers2.insert(-1, 'rms')
   
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------   
# After labelling an input file, write a summary showing the mean and standard deviation for each numeric item in the output records, over each time slice          |
# specified by the user. Do this chronologically, and then by label, if there is more than one time slice for a single label (so that means/stds for different time |
# slices can be easily compared visually).                                                                                                                          |
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def writeSummaryFile(df,transition,includeSubjectId,summary,sfilename,uniqueLabel):
  global subjectId, location
# Get the columns containing numeric items
  numCols = len(df.iloc[0])
  numericCols = []
  for i in range(1,numCols):
    if (isInt(df.iloc[0][i]) or isFloat(df.iloc[0][i])):
      numericCols.append(i)
  
# Use 'groupby' on the label to get the mean and standard deviation, for each time slice, for each label.
# 'includeSubjectId' is True if the user wants subjectId and sensor location included.
# Use 'thisLabel' to indicate if there is more than one time slice for the same label.
  ixx = 0
  labList = []
  prevLabel = ""
  byLabel = False
  
  for ix in range(1,len(transition)): 
    duration = df.iloc[transition[ix]][0] - df.iloc[ixx][0]
    if includeSubjectId:
      summaryLine = subjectId + ", " + df.iloc[ixx][numCols-1] + ", " + location + ", " + str(duration) + ", " 
    else:
      summaryLine = df.iloc[ixx][numCols-1] + ", " + str(duration) + ", " 
    
    for i in range(1,numCols-1):   
      if i in numericCols:
        result = df.iloc[ixx:(transition[ix]-1)].groupby('label')[headers[i]].mean().values
        summaryLine = summaryLine + str(result)[1:-1] + ", "
        result = df.iloc[ixx:(transition[ix]-1)].groupby('label')[headers[i]].std().values
        summaryLine = summaryLine + str(result)[1:-1] + ", "
    summaryLine = summaryLine.rstrip(" ")    
    summaryLine = summaryLine.rstrip(",")    
    summary.append(summaryLine.split(","))
    thisLabel = df.iloc[ixx,-1]
    if (thisLabel in labList) and (thisLabel != prevLabel):
      byLabel = True
    else:    
      labList.append(thisLabel)  
    prevLabel = thisLabel      
    ixx = transition[ix]  

# Write the summary records by time period into the summary file.  
  outRecs = []
  for s in summary:
    outRecs.append(s)
  df2 = pd.DataFrame(outRecs)
  writeOutputFile(df2,True,sfilename,True)

# Write a space line to the summary file, then sort the records by label type and write them again to summary, if there is at least one label for which there is
# more than one time slice.
  if byLabel:
    outRecs = [" "]
    df2 = pd.DataFrame(outRecs)
    writeOutputFile(df2,True,sfilename,False)
    outRecs = []
    del summary[0]  
    if includeSubjectId:
      summary = sorted(summary, key=lambda x: x[1])
    else:
      summary = sorted(summary, key=lambda x: x[0])
    for s in summary:
      s = ', '.join(s)
      outRecs.append(s)
    df2 = pd.DataFrame(outRecs)
    writeOutputFile(df2,True,sfilename,False)

def writeLabelledFile(df,xfilename):
  global row, activities, newTime, firstAct, transVal, transition, numCols, getRms, outRecs, summary
  
  summary = []
  summaryList = summaryHead
# Create a header line for the summary file
  for i in range(len(numericCols)):
    summaryList+=["Mean" + str((i+1))] + ["Std" + str((i+1))]
  if getRms:  
    summaryList+=["Rms Mean"] + ["Rms Std"]
  summary.append(summaryList)
  
# For each record in the subset of records from the input file chosen by the user :
#  Set the timestamp - for every time slice after the first one, the timestamp of each record will be amended. The timestamp of the first record in a time slice
#  is set to the timestamp of the last record of the previous time slice (except for the first time slice) plus one second or one minute, depending on whether the 
#  input file's timestamps are at second or minute level. All subsequent timestamps in the time slice increment from this first value.
#  Append a root mean square value, if requested.
#  Append the label chosen by the user for the time slice (held in 'ivals').
#  Skip any records with a label of 'Other'.
# Make a note of the locations in the dataframe where transitions occur from one label to the next, for creating the summary file.
# All records for the output file are stored in outRecs.
  firstAct, replaceTime = True, False
  outRecs, activities, transition, transVal, iy, ix = [], [], [0], 0, 0, 0
  for index, row in df.iterrows():  
    if replaceTime:
      saveTime = iTime  
    iTime = row[0] 
    if ivals[iy][1] == "Other":
      if not replaceTime:
        newTime = iTime
        replaceTime = True
      writeRow = False
    else:
      writeRow = True
      if replaceTime:
        if(iTime != saveTime):
          newTime = newTime + timedelta(**tPeriod)
      else:
        newTime = iTime
    if getRms:
      svm = 0    
      for i in range(1,numCols): 
        if i in rmsCols:
          svm+=float(row[i])**2
      svm=svm**0.5
    if (iTime <= ivals[iy][0]): 
      if writeRow:  
        createRecord(iy)      
    else:
      ix+=1
      if ix < half:
        if writeRow: 
          createRecord(iy)          
      else: 
        ix=0
        if ivals[(iy+1)][1] != "Other":
          createRecord(iy+1)
        iy+=1
#        if not isDatetime(str(ivals[iy][0])):
#          break        

  transition.append(-1)  

# Write the output file  
  df = pd.DataFrame(outRecs,columns=headers2)
  writeOutputFile(df,True,xfilename,True)
  return df
  
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# Append a label to each record in a subset of records from an input file selected by the user. Write two output files - one with the data, and a summary. |
# When loading the data the user selects which columns to process, whether to scale data, and the proportion of input records to keep.                     |
# They can add a root mean square value to output records, from a chosen set of input numeric values.                                                      |
# The user then selects time slices to include in the output file, from a plot, and allocates the label to append to each time slice.                      |
# A subject id and sensor location can be included in a summary file, if desired.                                                                          | 
# The summary file contains the means and standard deviations for each variable for each block of label - in time order and then                           |
# grouped by label type.                                                                                                                                   |
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
def labelFile(filename):
  global options, ivals, numCols, startTime, stopTime, summary, row, svm, freq, dForm, df, newTime, activities, headers, numericCols
  global writer, total, transVal, transition, firstAct, uniqueLabel, dFormOrig, getRms, rmsCols, headers2, si, dfScaled, colNums
  global perMinute, outRecs, csvFile, firstIsCsv, subjectId, location, dfNoScale, summaryHead, twoOutputs

  firstIsCsv = csvFile  

# Ask the user if they wish to include a root mean square value in the output file, and if so, which columns to base it on.
  procRms()
    
  ivals = [[0] * 2 for i in range(100)]

# Create a list of labels for the user to choose from
  options = setupList("Label") 
  print("\nDisplaying data file for label selection ...")
  print("Note - if the magnifier is used click y-values well above/below clicks used for label selection.")

# The user selects time slices from a plot of the data, and specifies the label to be appended for each time slice  
  df = plotData(df,0,0,False,False,'Select timestamps of transitions between activities using mouse left-click. Finish inputs with mouse right-click. Remove entry with delete/backspace.')

# Ask if a subjectid (eg name) and sensor location should be included in the summary file
  if getYNInput("\nInclude SubjectId and sensor location in the summary file? (Y/N) - "):
    includeSubjectId = True
  else:
    includeSubjectId = False  
  
  if includeSubjectId: 
    subjectId = getSubjectId()
    print("\nSelect sensor location : ")
    options = setupList("Location") 
    location = letUserPick(options) 
    locval = location[-3:-1]
    summaryHead = ["Subject","Label","Location","Duration"]
  else:  
    summaryHead = ["Label","Duration"]

# Get the folder and filenames for the output files
  defaultFolder = os.path.dirname(filename)
  folder = selectFolder(defaultFolder,"\nSelect the folder to create the output files in (D) for - " + defaultFolder + " or select folder (S) (D/S) - ")
  response = "C"
  while response == "C":
    xfilename, fName = getNewFilename("",folder,"Enter output filename")
    response = checkFileExists(xfilename,False,False)
  response = "C"
  while response == "C":   
    fName = fName+"_sum"  
    sfilename, fName = getNewFilename(fName,folder,"Enter output summary filename (CR for "+fName+")")
    response = checkFileExists(sfilename,False,False)

  print("\nPlease wait, processing data ...")
# Initialse stats variables
  rStd, total = 0, 0

# 'tPeriod' defines the time period to add to a timestamp when transitioning from one time slice to the next
  if "%S" in dFormOrig:
    tPeriod = {'quantity': '1', 'time': 'seconds'}
  else:
    tPeriod = {'quantity': '1', 'time': 'minutes'}
  tPeriod = {tPeriod['time']: int(tPeriod['quantity'])}  

# If the user wants both scaled and unscaled output files, produce both (if the user only requested one output, this will already be held in 'df').
  if twoOutputs:
    fn0, fn1 = os.path.splitext(os.path.abspath(xfilename))
    xfilenameNS = fn0 + "NoScale" + fn1
    fn0, fn1 = os.path.splitext(os.path.abspath(sfilename))
    sfilenameNS = fn0[:-4] + "NoScale_sum" + fn1
    dfNoScale = writeLabelledFile(dfNoScale,xfilenameNS)
    writeSummaryFile(dfNoScale,transition,includeSubjectId,summary,sfilenameNS,uniqueLabel)

  df = writeLabelledFile(df,xfilename)
  writeSummaryFile(df,transition,includeSubjectId,summary,sfilename,uniqueLabel)

# Display a plot of the output file with the specified activities if the user wishes.
  if getYNInput("\nPlot labelled data (Y/N) : "): 
    ind = 1
    for ac in uniqueLabel:
      if ac.upper() != "OTHER":
        df.replace(ac,ind,inplace=True)
        ind+=1
    if scalePlot:
      scaler = RobustScaler()
      scaler = scaler.fit(df[scaleColumns])
      df.loc[:, scaleColumns] = scaler.transform(df[scaleColumns].to_numpy())

    numCols = len(df.iloc[0])
    colNums.append(numCols-1)
    numericCols = list(range(numCols-1))
    
    headers = [f'Col {i}' for i in range(1,numCols)] 
    headers.insert(0,"Time")
    df.columns = headers
    
    plotData2(df,True)

#--------------------------------------------------------------------------------------------------------------------
# Get the user to select the data file being processed. A separate file explorer window pops up from which they can |
# click on the file, then on 'open'. Note if the file is 'csv'. Put the file contents (or a subset) in a dataframe. |
#--------------------------------------------------------------------------------------------------------------------
def getInputFile(purpose,inText):
  global csvFile
  filename = ""
  while filename == "":
    print(inText)   
    root = Tk(); root.withdraw()
    filename = fd.askopenfilename(filetypes=[("Input file", "*.csv .xls .xlsx")])
    root.destroy()
    print("\nFile selected - ",filename)    
    _ , inputFileType = os.path.splitext(filename)
    if inputFileType == ".csv":
      csvFile = True
    else:  
      csvFile = False
    getData(filename)
  return filename

#-----------------------------------
# Get a new filename from the user |
#-----------------------------------
def getNewFilename(defaultFname,folder,txt):
  global csvFile   
  if csvFile:
    extension = ".csv"
  else:  
    extension = ".xlsx"

  iPath = folder + "/"
  txt = txt + " (" + extension + " will be appended to it)"
  print(" ")  
  print(txt)
  print("(Folder used will be ",iPath,")")
  
  newFile = ""
  while newFile == "":    
    newFile = input(" - ")
    if newFile == "":
      newFile = defaultFname
    if len(newFile) > 0:
      try:
        fName = newFile
        newFile = newFile + extension
        validate_filename(newFile)
        newFile = iPath + newFile
      except ValidationError as e:
        print("Invalid filename entered - ",newFile)
        print("{}\n".format(e), file=sys.stderr)
        newFile = ""
    
  return(newFile, fName)

#--------------------------------------------------------------------------------------------------------
# Show the user an input record, then get them to select a single column, which may need to be numeric. |
#--------------------------------------------------------------------------------------------------------
def selectSingleColumn(txt,numericReqd):
  global df, numericCols
  print("Example row - ")
  ix = 0
  for co in df.iloc[5]:
    print("col ",ix," -    ",co)
    ix+=1

  numcols = len(df.iloc[0])
  while True:
    targetCol = input(txt)
    if targetCol == "":
      targetCol = numcols-1
    try:
      targetCol = int(targetCol)    
      if numericReqd:
        if targetCol in numericCols:
          break
      else:
        if (targetCol > -2) and (targetCol < numcols):
          break
    except ValueError:
      print("Invalid entry")  
  return targetCol      

#------------------------------------------------------------------------------------------------------------------------------------------------------
# When pre-processing physiological data, ask the user whether blocks of data are processed per minute, or per number of records - the mean value     |
# of blocks of data is calculated on this basis, for determining whether or not to amend data values (we know we are dealing with an input file       |
# with timestamps at a minute, rather than second, level.                                                                                             |                                                                             |
#------------------------------------------------------------------------------------------------------------------------------------------------------
def getMinuteBlockResponse():
  print(" ")
  byMinute, byBlock, perBlock = False, False, 0
  while True:
    txt = "Process data on a minute by minute basis (M) or by blocks containing a specified number of records (B) : "    
    response = input(txt).upper()  
    if response == "M":
      byMinute = True
      break
    if response == "B":
      byBlock = True
      while True:    
        try:
          perBlock = int(input("Specify number of records per block of data (min 2) - "))
          if (perBlock > 1) and (perBlock <= freq):
            break
        except ValueError:
          print("Invalid entry. Must be an integer > 1 and <= ",freq)
      break
  return byMinute, byBlock, perBlock

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# When pre-processing physiological data, ask the user whether blocks of data are processed per minute, per number of seconds, or per number of records | 
# - the mean value of blocks of data is calculated on this basis, for determining whether or not to amend data values.                                  |                                                                                          |                                                                             |
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def getSecondsBlockResponse():
  print(" ")
  perBlock, secondsPerBlock = 0, 0
  byMinute, bySeconds, byBlock = False, False, False
  while True:
    txt = "Process data on a minute by minute basis (M), by blocks of seconds (S) or by blocks containing a specified number of records (B) : "    
    response = input(txt).upper()  
    if response == "M":
      byMinute = True
      break
    if response == "B":
      byBlock = True
      while True:    
        try:
          perBlock = int(input("Specify number of records per block of data (min 2) - "))
          if (perBlock > 1) and (perBlock <= freq):
            break
        except ValueError:
          print("Invalid entry. Must be an integer > 1 and <= ",freq)
      break
    if response == "S":
      bySeconds = True
      while True:    
        try:
          secondsPerBlock = int(input("Specify number of seconds per block of data (min 2) - "))
          if (secondsPerBlock > 1) and (secondsPerBlock <= freq):
            break
        except ValueError:
          print("Invalid entry. Must be an integer > 1 and <= ",freq)
      break
      
  return byMinute, bySeconds, byBlock, perBlock, secondsPerBlock


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Amend the values in one numeric column of the input file if, on a block of data basis, the mean value for one block differs from the mean value for the period     |
# of one block from two blocks earlier, by more than a specified percentage. If this is the case set the values for the previous block to the same as the values for |
# the current block. Blocks are defined per minute, per number of seconds, or per number of records, as specified by the user.                                       |                                                                                                        |
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
def preProcessPhysiological(filename): 
  global colNums, df, numericCols, csvFile, firstIsCsv, freq, perMinute

  if perMinute:
    print("Input records are recorded at a 'per minute' level")
  else:
    freq = 60*freq  
  print("Records per minute - ",freq)

  if perMinute:
    bySeconds = False
    byMinute, byBlock, perBlock = getMinuteBlockResponse()
  else:  
    byMinute, bySeconds, byBlock, perBlock, secondsPerBlock = getSecondsBlockResponse()
  
  if byMinute:  
    print("\nData values will be changed when the mean value for any given minute of data differs by more than a specified percentage from the mean value")
    print("for the data over a period of one minute, from 2 minutes earlier.")
  if byBlock:
    print("\nData values will be changed when the mean value for any given block of data differs by more than a specified percentage from the mean value")
    print("for the data over a period of one block, from 2 blocks earlier.")
  if bySeconds:
    print("\nData values will be changed when the mean value for any given block of seconds of data differs by more than a specified percentage from the mean value")
    print("for the data over a period of one block of seconds, from 2 blocks of seconds earlier.")
  
  percent = getPercent("\nEnter the percentage difference value that results in the data being changed in the range 5 to 95 (excluding the percentage sign. CR for default = 50%) : ",5,95,50)
  firstIsCsv = csvFile 

# Get the output filename  
  defaultFolder = os.path.dirname(filename)
  folder = selectFolder(defaultFolder,"\nSelect the folder to create the output files in (D) for - " + defaultFolder + " or select folder (S) (D/S) - ")
 
  response = "C"
  while response == "C":
    newFile, fName = getNewFilename("",folder,"Enter output filename")
    response = checkFileExists(newFile,False,False)

# If there is more than one column of numeric data, ask the user which column to process
  if len(numericCols) > 1:
    targetCol = selectSingleColumn('\nEnter the number of the column to pre-process (CR for last column; first column is column 0) : ',True)
  else:
    targetCol = int(numericCols[0]) 

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------      
# Calculate the mean value (t1) for the selected column for each block of data. Compare it with the mean value from two blocks earlier (t3). If the percentage change   |
# is greater than the percentage specified by the user (percent), then change the values in that column for the previous block to those of the current block.           |
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ix, t1, t2, t3, st1, st2 = 0, 0, 0, 0, 0, 0
  stime = df.iloc[0,0]
  dflen = len(df)-1
  found = False
  while ix < dflen: 
    ix2, sumV = 0, 0  
    st2 = st1
    st1 = ix  
    if byMinute:
      while (stime.minute == df.iloc[ix,0].minute) and (ix < dflen):
        sumV+=df.iloc[ix,targetCol]
        ix2+=1
        ix+=1  
    elif byBlock:    
      while (ix2 < perBlock) and (ix < dflen):
        sumV+=df.iloc[ix,targetCol]
        ix2+=1
        ix+=1  
    else:   
      while ((df.iloc[ix,0]-stime).total_seconds() < secondsPerBlock) and (ix < dflen):
        sumV+=df.iloc[ix,targetCol]
        ix2+=1
        ix+=1  

    if ix2 > 0:
      t3 = t2
      t2 = t1
      t1 = sumV/ix2  
      stime = df.iloc[ix,0]
      if t3 > 0:
        percentChange = (abs(t1-t3)/t3)*100
        if percentChange > percent:
          print("Changing data at - ",df.iloc[st2][0])
          ix3 = 0
          while st2 < st1:
            df.iat[st2,targetCol] = df.iloc[st1+ix3][targetCol]
            st2+=1
            ix3+=1
            found = True

# If no changes were made, with the given percentage specified by the user, stop.
  if not found:
    print("\nNo data was changed at the specified percentage. Terminating.")
  else:

# Write the changed data to the output file chosen by the user
    writeOutputFile(df,True,newFile,True)

# Display a plot of the changed data (just the timestamp and column that was changed)
    numericCols = [0,targetCol]
    plotData2(df,False)

# Write a dataframe to the output file chosen by the user. The file type will be the same as the input file type.
# For an Excel output file, if more than one dataframe is being written, 'startRow' is set to the end of the file after the previous dataframe was written,
# to append rows, rather than overwrite (if the user is overwriting the file it will have been previously deleted).
def writeOutputFile(df,firstFile,newFile,writeMessage):
  global firstIsCsv
  if writeMessage: 
    print("\nWriting to ",newFile)
  if firstIsCsv:
    df.to_csv(newFile, encoding='utf-8', index=False, header=False,mode='a', quotechar=' ')  
  else:
    writer = pd.ExcelWriter(newFile, engine='openpyxl')
    if firstFile:
      startRow = 0
    else:
      writer.book = load_workbook(newFile)
      writer.sheets =  {ws.title: ws for ws in writer.book.worksheets}      
      startRow = (writer.sheets['Sheet1'].max_row)+1
    df.to_excel(writer, sheet_name='Sheet1', index=False,header=False,startrow=startRow)
    writer.save()

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# Combine multiple files into one output file, by appending each file after the first one to the end of the output file.
# After the first file, the timestamp for the first record of the next file is set to the timestamp of the last record of the previous file, plus one second or 
# one minute (depending on the whether timestamps in the first file are at a second or minute level), and remaining timestamps increment from that first value.
# Some options chosen by the user for the first file can be used for subsequent files.
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
def combineFiles(xfilename):
  global numCols, dForm, colNums, tPeriod, askUser, smd, scalePlot, perSec, si, df, csvFile, perMinute, firstIsCsv, newFile, dFrac
  savedSmd, savedSi, savedScalePlot, saveddFrac, savedNumCols = smd, si, scalePlot, dFrac, numCols
  firstIsCsv = csvFile  
  
# Get the output filename from the user for combining all the input files into.
  defaultFolder = os.path.dirname(xfilename)
  folder = selectFolder(defaultFolder,"\nSelect the folder to create the output files in (D) for - " + defaultFolder + " or select folder (S) (D/S) - ")

  response = "C"
  while response == "C":
    newFile, fName = getNewFilename("",folder,"Enter output filename")
    response = checkFileExists(newFile,False,False)

# Write the first file to the output file
  writeOutputFile(df,True,newFile,True)

# Get the last record from the first input file. 
  saveFirst, saveLast = getFirstLastRecords(df)
 
# For each subsequent input file append all the records to the end of the output file, replacing the timestamp with one that begins 1 second/minute after the end of the
# previous input file, and incrementing it by one second/minute every time the second/minute value changes in the input timestamp.
  filename = "x"
# The user keeps selecting input files until finished - at which point they select 'Cancel' in the Explorer window rather than 'Open'.  
  while filename != "":
# Get the next input file  
    print("\nSelect next input data file ('Cancel' when finished entering files)")
    root = Tk(); root.withdraw()
    filename = fd.askopenfilename(filetypes=[("Input file", "*.csv .xls .xlsx")])
    root.destroy()
    if filename != "":
      print("\nFile selected - ",filename)
      if getYNInput("\nUse the same responses as for the first file for Switch Month Day, Scaling and Proportion of records to keep (Y/N) : "):
        askUser = False
        smd, si, scalePlot, dFrac = savedSmd, savedSi, savedScalePlot, saveddFrac
      else:
        askUser = True  
        
      _ , inputFileType = os.path.splitext(filename)
      if inputFileType == ".csv":
        csvFile = True
      else:  
        csvFile = False

      getData(filename)
      firstRecord, lastRecord = getFirstLastRecords(df)
      
# Adjust the timestamp values by the required amount      
      if perMinute:
        numMinutes = int((saveLast - firstRecord).total_seconds()/60)+1
        df['Time'] = df['Time'] + pd.Timedelta(minutes=numMinutes)     
      else:     
        numSeconds = int((saveLast - firstRecord).total_seconds())+1
        df['Time'] = df['Time'] + pd.Timedelta(seconds=numSeconds)     

# Write the input file to the output file (append to the end)      
      writeOutputFile(df,False,newFile,True)
      saveFirst, saveLast = getFirstLastRecords(df)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# When merging two files, for each record append the required columns from the second file to those from the first file. If the frequency of the second file is lower      |
# than for the first file, add the data from one record of the second file to multiple records from the first file.                                                        |
# Calculate the whole number mutiple of the frequency of the first file divided by the frequency of the second, and the remainder as a proportion of the frequency of the  |
# second file.                                                                                                                                                             | 
# Add the whole number mutiple number of records from the second file to each record from the first file, and for each time this is done add the remainder to a            | 
# running total. When the remainder exceeds 0.5 add an extra record from the second file to the current first file record.                                                 |
# eg if the frequency is 6 (records per second) for the first file and 5 for the second file, then we have a whole number divisor of '1', and 1 record left over, which is |
# 0.2 (1/5) of the second frequency. We therefore append 1 record from the second file to one record from the first file, and increment a sum by 0.2. Each time the sum    |
# exceeds 0.5 we append a second record from the second file to the current record from the first file, then subtract 1 from the sum.                                      |
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def addNextRecs():
  global freq1, freq2, dfxxx, dfyyy, outRecs
  part = (freq1/freq2) % 1
  whole = (freq1/freq2) // 1
  diff = 0.0
  ix = 0
  ix4 = 0
  
  while ix < freq1:
    ix3 = 0
    addVals = ', '.join(str(item) for item in dfyyy[ix4])
    aVs = list(addVals.split(","))
    while ix3 < whole:
      newRow = dfxxx[ix] + aVs
      outRecs.append(newRow)
      ix3+=1
      ix+=1
      if ix >= freq1:
        break
    if ix >= freq1:
      break
    ix4+=1  
      
    diff+=part 
    if diff > 0.5:
      newRow = dfxxx[ix] + aVs
      outRecs.append(newRow)          
      ix+=1
      diff-=1

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Append the records from one file to those of another file (excluding the timestamp of the second file, and allowing the user to specify which columns to                  | 
# include from each file). If one file has a higher frequency than the other (number of records per minute), make this the primary file - the timestamp will be taken       |
# from this file, and the data from it will come first in each record. If the frequencies are the same, then the first file specified by the user is the primary file.      |
# The user selects the time slice to process from a plot of the primary file. If the two files are synchronised no further timestamp processing is required.                |
# If the two files are not synchronised (time-wise) then the user selects the start time from a plot of the secondary file - the user must ensure an appropriate start time |
# is chosen, as otherwise merging the files becomes meaningless. eg if a user wore two sensors, an accelerometer and a heart rate monitor, and they were not time           |
# synchronised, then the user must know what times both sensors are set to before meging the data, otherwise the merged readings will not reflect the readings that both    |
# sensors were recording at a specific time. If the primary file has higher frequency than the secondary file, multiple records from the secondary file may be appended to a|
# single record from the primary file.                                                                                                                                      |
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def mergeFiles(filename1):
  global freq1, headers, numCols, perMinute, df, firstIsCsv, filename, csvFile, scalePlot, dfScaledPlot
  global freq2, askCols, colNums, freq, csvFile, dfyyy, dfxxx, outRecs

  firstIsCsv = csvFile  

# Save the frequency and filename of the first file
  if not perMinute:
    freq = freq*60
  freq1 = freq  
  filename1 = filename
  dfx = df.copy()
  sp1 = scalePlot
  if sp1:
    dfxSP1 = dfScaledPlot.copy()

# Get the user to choose the second file   
  askCols = True  
  filename = getInputFile(purpose,"\nSelect second data file")
  sp2 = scalePlot
  if sp2:
    dfxSP2 = dfScaledPlot.copy()

  if not perMinute:
    freq = freq*60

# Check which file has the greater frequency (if either). Set 'df' to contain the primary file data, and 'df2' the secondary file data
  if freq <= freq1:
    fileSwitch = False
    df2 = df.copy()   
    df = dfx
    filename2 = filename
  else:  
    fileSwitch = True  
    df2 = dfx.copy()   
    filename2 = filename1
    filename1 = filename
    sp2 = sp1
    if sp2:
      dfxSP2 = dfxSP1.copy()  
    sp1 = scalePlot
    if sp1:
      dfxSP1 = dfScaledPlot.copy()    
   
# Get the timestamps of the first and last records for each file. If the last timestamp from one file is earlier than the first timestamp from the other file then we know they
# are not synchronised, otherwise we'll ask the user if they are synchronised.
  sTime,  eTime  = getFirstLastRecords(df)
  sTime2, eTime2 = getFirstLastRecords(df2)
  sTimex = max([sTime,sTime2])
  eTimex = min([eTime,eTime2])
    
  if (sTime > eTime2) or (sTime2 > eTime):
    synchronised = False
  else:  
    if getYNInput("\nAre the timestamps synchronised for the 2 files? Y/N "):
      synchronised = True  
      df  = df.loc[(df['Time'] >= sTimex) & (df['Time'] <= eTimex)]  
      df2 = df2.loc[(df2['Time'] >= sTimex) & (df2['Time'] <= eTimex)]  
      sTime, sTime2, eTime, eTime2 = sTimex, sTimex, eTimex, eTimex
    else:
      synchronised = False  

  scalePlot = sp1
  if scalePlot:
    dfScaledPlot = dfxSP1.copy()
  
# Get the user to select the time slice to be processed from a plot of the primary file
  df = plotData(df,sTime,eTime,True,False,'Select start/end times of the data of interest using mouse left-click. Finish inputs with mouse right-click. Remove entry with delete/backspace.')
  sTime = df.iloc[0,0]
  eTime = df.iloc[-1,0]

# If the times are not synchronised, get the user to select the start time for the secondary file from a plot
  if synchronised:
    sTime2 = sTime
    eTime2 = eTime
    df2 = df2.loc[(df2['Time'] >= sTime2) & (df2['Time'] <= eTime2)]  
  else:
    scalePlot = sp2
    if scalePlot:
      dfScaledPlot = dfxSP2.copy()
    df2 = plotData(df2,sTime2,eTime2,True,True,'Select the start time of the data of interest using mouse left-click. Finish input with mouse right-click. Remove entry with delete/backspace.')    
    sTime2 = df2.iloc[0,0]  
    eTime2 = df2.iloc[-1,0]

  defaultFolder = os.path.dirname(filename)
  folder = selectFolder(defaultFolder,"\nSelect the folder to create the output files in (D) for - " + defaultFolder + " or select folder (S) (D/S) - ")

# Get the name of the output file
  csvFile = firstIsCsv
  response = "C"
  while response == "C":
    newFile, fName = getNewFilename("",folder,"Enter output filename")
    response = checkFileExists(newFile,False,False)

  oldFreq2 = 1
  dfyy = df2.iloc[0]
  oldDfyyy = dfyy.values.tolist()

# Loop through all records from the primary file, minute by minute, appending the appropriate number of records from the secondary file to each primary file record.
# If the frequency of the secondary file exceeds that of the primary file for any given minute, warn the user and do not include the excess secondary file records.
  eTimex = sTime
  eTimey = sTime2
  firstWarn = True
  outRecs = []
  while eTimex < eTime:
      freq1 = 0
      while (freq1 == 0) and (eTimex < eTime):
        eTimex = eTimex + timedelta(minutes=1)
        eTimey = eTimey + timedelta(minutes=1)

# Get one minute's worth of data from each file      
        dfxx = df.loc[(df['Time'] >= sTime) & (df['Time'] < eTimex)]
        freq1 = len(dfxx)
        dfyy = df2.loc[(df2['Time'] >= sTime2) & (df2['Time'] < eTimey)]
        freq2 = len(dfyy)
                
# if the secondary file's frequency is greater than the primary file's for this minute, output a warning
        if freq2 > freq1:
          if firstWarn:
            print(" ")
            firstWarn = False
          print("Warning : lower frequency detected in ",filename," than in ", filename2, " at times ",sTime,"/",sTime2," respectively.")
          print("Excess rows will be trimmed from file2 at this time.")

        sTime  = eTimex
        sTime2 = eTimey

# If the secondary file has no records for the current minute, use the records from the previous minute.
      dfxxx = dfxx.values.tolist()    
      if freq2 == 0:
        freq2 = oldFreq2
        dfyyy = oldDfyyy
      else:
        dfyy = dfyy.iloc[: , 1:]
        dfyyy = dfyy.values.tolist()
        oldFreq2 = freq2
        oldDfyyy = dfyyy

# Add this minute's records to the output dataframe       
      addNextRecs()

# Write the output file
  df = pd.DataFrame(outRecs)
  writeOutputFile(df,True,newFile,True)

#-------------------------------------------------------
# Print the help text to the user's console, or a file |
#-------------------------------------------------------
def printHelpText(dummy):
  printTarget = ""
  while printTarget != "C" and printTarget != "F":
    printTarget = input("Output Help to Console (C) or file 'helptext.txt' in current folder (F) - ").upper()

  if printTarget == "F":
    with open('helptext.txt', 'w') as f:
      sys.stdout = f 
      print(helpText) 
  else:
    print(helpText)  

# Define the processing required, as specified by the user.
def setProcessingType():
# If 'help' is selected, output help text to the console or a file, 'helptext.txt', according to user preference.
  if "HELP" in purpose: 
    performProcessing = "printHelpText"
  elif "RUN NEURAL" in purpose:
    performProcessing = "runSavedKeras"
  elif "RUN KMEANS" in purpose:
    performProcessing = "runSavedKmeans"
  elif "RUN MACHINE" in purpose:
    performProcessing = "runSavedML"
  elif "CREATE KMEANS" in purpose:  
    performProcessing = "kmeansAnalysis"
  elif "CREATE MACHINE LEARNING" in purpose:  
    performProcessing = "machineLearnAnalysis"
  elif "CREATE NEURAL" in purpose:  
    performProcessing = "kerasAnalysis" 
  elif "COMBINE" in purpose:  
    performProcessing = "combineFiles"
  elif "PHYSIO" in purpose:  
    performProcessing = "preProcessPhysiological" 
  elif "MERGE" in purpose:  
    performProcessing = "mergeFiles" 
  elif ("LABEL CSV" in purpose): 
    performProcessing = "labelFile"
  elif ("SHOW HISTOGRAM" in purpose): 
    performProcessing = "showHistogram"
  else: 
    print("Terminating")
    exit()
    
  return performProcessing

#--------------------------------------------------------------------------------------------------------
# Plot a histogram of selected input data (numeric only). The user specifies the number of bins to use. |
#--------------------------------------------------------------------------------------------------------
def showHistogram(dummy):
  global df
  df = plotData(df,0,0,True,False,'Select the start and end times of the data of interest using mouse left-click. Finish input with mouse right-click. Remove entry with delete/backspace.')    

  numBins = getIntegerInput("\nEnter the number of bins to use in the range 2 to 100 (CR for default = 10) : ",2,100,10)
  cls = list(df.iloc[:,numericCols])
  clsdf = []
  for cl in cls:
    clsdf.append(df[cl])

  txt = "\nChange plot legend (currently - " + str(cls) + ")? Y/N - "    
  if getYNInput(txt):
    print(" ")
    pltLegend = []
    for cl in cls:
      txt = "Replace " + cl + " with - "
      newLine = ""
      while len(newLine) == 0:
        newLine = input(txt)
      pltLegend.append(newLine)
  else:
    pltLegend = cls
    
  txt = "\nAdd a title to the plot? Y/N - " 
  pltTitle = ""
  if getYNInput(txt):
    pltTitle = ""
    print(" ")
    while len(pltTitle) == 0:
        pltTitle = input("Enter plot title - ")
    plt.title(pltTitle)
    
  plt.style.use('seaborn-deep')
  plt.hist(clsdf, bins=numBins)  # density=False would make counts
  plt.ylabel('Frequency')
  plt.xlabel('Value')
    
  plt.legend(pltLegend)
  plt.show()

#-------------------
# End of functions |
#-------------------

#------------------
# Main processing |
#------------------

processingDone = []
firstRun = True
configChange = False

# Keep looping, performing required processing until the user selects 'exit'.
while True:
# Initialise variables
  sTimex, eTimex, perSec = 0, 0, 0
  startTime, hasHeader, headers, dForm, freq, numCols, getRms, askCols, askUser, smd, si = 0, False, "", "", 0, 0, False, True, True, False, ""

# Get the contents of the config file 'sensorcodeConfigFile.txt' (or create it if it doesn't exist)
  if firstRun or configChange:
    getConfigs("")
    configChange = False
    
# Ask the user what processing they are performing 
  print("\nSelect required processing : ")
  options = setupList("Purpose") 
  purpose = letUserPick(options).upper() 

  performProcessing = setProcessingType()

  if performProcessing == "printHelpText":
    filename = "dummy"
  else:  
# Load required run time libraries
    if performProcessing not in processingDone:
      loadLibraries()
      processingDone.append(performProcessing)

# Get the (first) input file from the user
    if ("Combine" in purpose) or ("Merge" in purpose):
      filename = getInputFile(purpose,"\nSelect first input data file")
    else:
      filename = getInputFile(purpose,"\nSelect input data file")
      
    firstRun = False
    
# Perform the required processing, as requested by the user
  eval(performProcessing + "(filename)")
  
#--------------
# End of code |
#--------------


